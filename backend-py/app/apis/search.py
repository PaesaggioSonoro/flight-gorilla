from collections import defaultdict, deque

from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from flask_restx import Namespace, Resource, fields, reqparse, marshal
import datetime
import uuid

from sqlalchemy.orm import joinedload

from app.apis.search_utils import generate_journey, filter_journeys, sort_journeys, get_airports, \
    lowest_price_multiple_dates, check_duplicate_flight
from app.extensions import db
from app.models import Flight
from app.models.airport import Airport
from app.models.booking import BookingDepartureFlight, Booking, BookingReturnFlight
from app.models.flight import Route

api = Namespace('search', description='Flight search operations')
import math

def str_to_bool(value: str) -> bool:
    if isinstance(value, bool):
        return value
    if value.lower() in {'true', '1', 'yes'}:
        return True
    elif value.lower() in {'false', '0', 'no'}:
        return False
    raise ValueError(f"Invalid boolean value: {value}")

# Base parser for common search parameters used across different search endpoints
def build_base_search_parser():
    parser = reqparse.RequestParser()
    # Required parameters for any flight search
    parser.add_argument('departure_id', type=int, required=True,
                        help='Departure id', location='args')
    parser.add_argument('departure_type', type=str, choices=('airport', 'city'), required=True,
                        help='Type of departure location: "airport" or "city"', location='args')
    parser.add_argument('arrival_id', type=int, required=True,
                        help='Arrival id', location='args')
    parser.add_argument('arrival_type', type=str, choices=('airport', 'city'), required=True,
                        help='Type of arrival location: "airport" or "city"', location='args')
    # Optional filters and sorting parameters
    parser.add_argument('airline_id', type=str,
                        help='Filter by specific airline ID', location='args')
    parser.add_argument('price_max', type=float,
                        help='Maximum price (economy class)', location='args')
    parser.add_argument('departure_time_min', type=str,
                        help='Minimum departure time (HH:MM)', location='args')
    parser.add_argument('departure_time_max', type=str,
                        help='Maximum departure time (HH:MM)', location='args')
    parser.add_argument('order_by', type=str, choices=('price', 'duration', 'stops'),
                        help='Order by field (price_economy, duration_minutes, stops)', location='args')
    parser.add_argument('order_by_desc', type=str_to_bool, default="False",
                        help='Order by field descending', location='args')
    # Pagination parameters
    parser.add_argument('page_number', type=int,
                        help='Pagination offset (for large result sets)', location='args')
    parser.add_argument('limit', type=int,
                        help='Limit the number of results returned for page', location='args')
    parser.add_argument('max_transfers', type=int, default=3)
    return parser

# Parser for exact date searches
flight_search_parser = build_base_search_parser()
flight_search_parser.add_argument('departure_date', type=str, required=True,
                                 help='Departure date (DD-MM-YYYY)', location='args')

# Parser for flexible date searches (month-based)
flexible_date_search_parser = build_base_search_parser()
flexible_date_search_parser.add_argument('departure_date', type=str, required=True,
                                         help='Departure date (MM-YYYY)', location='args')

segment_model = api.model('FlightSegment', {
    'id': fields.String(description='Flight segment ID'),
    'flight_number': fields.String(description='Flight number for this segment'),
    'airline_name': fields.String(description='Airline name for this segment'),
    'airline_id': fields.String(description='Airline ID for this segment'),
    'departure_airport': fields.String(description='Departure airport code for this segment'),
    'arrival_airport': fields.String(description='Arrival airport code for this segment'),
    'departure_time': fields.DateTime(description='Departure time for this segment'),
    'arrival_time': fields.DateTime(description='Arrival time for this segment'),
    'duration_minutes': fields.Integer(description='Flight duration in minutes for this segment'),
    'price_economy': fields.Float(description='Economy class price for this segment'),
    'price_business': fields.Float(description='Business class price for this segment'),
    'price_first': fields.Float(description='First class price for this segment'),

    'aircraft_name': fields.String(description='Aircraft name for this segment'),
    'gate': fields.String(description='Departure gate for this segment', allow_null=True),
    'terminal': fields.String(description='Departure terminal for this segment', allow_null=True),
})

layover_model = api.model('Layover', {
    'airport': fields.String(description='Layover airport code'),
    'duration_minutes': fields.Integer(description='Layover duration in minutes'),
})

journey_model = api.model('Journey', {
    'departure_airport': fields.String(description='Origin airport code for the journey'),
    'arrival_airport': fields.String(description='Destination airport code for the journey'),
    'duration_minutes': fields.Integer(description='Total journey duration in minutes'),
    'price_economy': fields.Float(description='Total economy class price for the journey'),
    'price_business': fields.Float(description='Total business class price for the journey'),
    'price_first': fields.Float(description='Total first class price for the journey'),
    'is_direct': fields.Boolean(description='True if the journey is direct, false otherwise'),
    'stops': fields.Integer(description='Number of stops (layovers)'),
    'segments': fields.List(fields.Nested(segment_model), description='List of flight segments in the journey'),
    'layovers': fields.List(fields.Nested(layover_model), description='List of layovers in the journey'),
})

search_output_model = api.model('SearchOutput', {
    'journeys': fields.List(fields.Nested(journey_model), description='List of flight journeys'),
    'total_pages': fields.Integer(description='Total number of pages for pagination'),
})

@api.route('/flights')
class FlightSearch(Resource):
    @api.doc(security=None)
    @api.expect(flight_search_parser)
    @api.response(200, 'Created', [search_output_model])
    @api.response(400, 'Bad Request')
    def get(self):
        """Search for flights based on departure/arrival airports and date using RAPTOR algorithm"""
        args = flight_search_parser.parse_args()

        # Try to get user ID if authenticated, but don't require authentication
        args['user_id'] = None
        try:
            verify_jwt_in_request(optional=True)
            args['user_id'] = get_jwt_identity()
        except Exception:
            current_user = None

        # Validate departure date format and ensure it's not in the past
        try:
            departure_date = datetime.datetime.strptime(args['departure_date'], '%d-%m-%Y').date()
        except ValueError:
            return {'error': 'Invalid departure date format. Use DD-MM-YYYY', 'code': 400}, 400

        if departure_date < datetime.datetime.now().date():
            return {'error': 'Departure date cannot be in the past', 'code': 400}, 400

        # Initialize results container
        unfiltered_departure_journeys = []

        # Get valid departure and arrival airports based on search criteria
        departure_airports, arrival_airports, error = get_airports(args)
        if error:
            return error

        # Generate journeys for each valid airport pair
        for departure_airport in departure_airports:
            for arrival_airport in arrival_airports:
                # Use RAPTOR algorithm to find optimal routes
                departure_results = generate_journey(
                    departure_airport,
                    arrival_airport,
                    departure_date,
                    max_transfers=int(args['max_transfers']),
                    args=args
                )
                unfiltered_departure_journeys.extend(departure_results)
        
        # Apply filters and sorting based on user preferences
        departure_journeys = filter_journeys(unfiltered_departure_journeys, args)
        departure_journeys = sort_journeys(departure_journeys, args)

        # Store original length for pagination calculation
        original_len = len(departure_journeys)
        
        # Apply pagination if requested
        args['limit'] = args['limit'] if args['limit'] else 10
        if args['page_number'] and args['limit']:
            start = (args['page_number'] - 1) * args['limit']
            end = start + args['limit']
            if start >= len(departure_journeys) or start < 0:
                departure_journeys = []
            else:
                end = min(end, len(departure_journeys))
                departure_journeys = departure_journeys[start:end]

        # Return paginated results with total page count
        return marshal({'journeys':departure_journeys,'total_pages':math.ceil(original_len/args['limit'])},search_output_model), 200

@api.route('/flexible-dates')
class FlexibleFlightSearch(Resource):
    
    def _calculate_dates(self,date):
        """Calculate the start and end dates for a given month"""

        start_date = datetime.date(date.year, date.month, 1)
        if date.month == 12:
            end_date = datetime.date(date.year + 1, 1, 1) - datetime.timedelta(days=1)
        else:
            end_date = datetime.date(date.year, date.month + 1, 1) - datetime.timedelta(days=1)
        
        date_range = [start_date + datetime.timedelta(days=i) for i in range((end_date - start_date).days + 1)]
        
        return date_range
    
    
    #generare ricerca per nazione -> città 
    @api.doc(security=None)
    @api.expect(flexible_date_search_parser)
    @api.response(200, 'OK')
    def get(self):
        """Get minimum prices for each day in a month for a given departure and arrival airport"""
        args = flexible_date_search_parser.parse_args()
        args['user_id'] = None
        try:
            verify_jwt_in_request(optional=True)
            args['user_id'] = get_jwt_identity()
        except Exception:
            current_user = None
        # Parse and validate date
        departure_journeys =[]
        try:
            departure_date = datetime.datetime.strptime(args['departure_date'], '%m-%Y').date()
        except ValueError:
            return {'error': 'Invalid departure date format. Use MM', 'code': 400}, 400

        # Get airports
        departure_airports, arrival_airports ,error = get_airports(args)
        if error:
            return error
            
            
        departure_date_range = self._calculate_dates(departure_date)
        today_d = datetime.date.today()
        if departure_date.month == today_d.month and departure_date.year == today_d.year:
            # If the month is the current month, filter out past dates
            departure_date_range = departure_date_range[today_d.day:]
            # Add None as many as the number of days in the month skipped
            departure_journeys = [None] * today_d.day

        # for each day in the range of dates, generate journeys
        possible_journeys = lowest_price_multiple_dates(
            departure_date_range,
            departure_airports,
            arrival_airports,
            args
        )
        departure_journeys.extend(possible_journeys)

        return departure_journeys, 200
