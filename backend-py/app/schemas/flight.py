from attr import attributes
from marshmallow import validates_schema, ValidationError, post_dump
from sqlalchemy import exists, or_

from app.extensions import ma, db
from app.models.booking import BookingReturnFlight, BookingDepartureFlight
from app.models.flight import Flight, Route, FlightExtra
from app.models.airport import Airport
from app.models.airlines import Airline, AirlineAircraft
from app.schemas.airport import AirportSchema
from app.schemas.airline import AirlineSchema
from app.schemas.airline import AirlineAircraftSchema
from app.schemas.airline import RouteSchema
import datetime



class FlightSchema(ma.SQLAlchemyAutoSchema):

    airline = ma.Nested(AirlineSchema, dump_only=True)
    departure_airport = ma.Nested(AirportSchema, dump_only=True)
    arrival_airport = ma.Nested(AirportSchema, dump_only=True)
    flight_number = ma.String(dump_only=True)
    aircraft = ma.Nested(AirlineAircraftSchema, dump_only=True)
    booked_seats = ma.List(ma.String(), attribute="booked_seats", dump_only=True)
    checkin_start_time = ma.DateTime(required=False)
    checkin_end_time = ma.DateTime(required=False)
    boarding_start_time = ma.DateTime(required=False)
    boarding_end_time = ma.DateTime(required=False)
    
    class Meta:
        model = Flight
        load_instance = True
        include_fk = True

    @validates_schema
    def validate_times_and_foreign_keys(self, data, **kwargs):
        # Validate departure/arrival times
        departure_time = data.get("departure_time")
        arrival_time = data.get("arrival_time")

        if departure_time and departure_time < datetime.datetime.now(datetime.UTC):
            raise ValidationError("Departure time cannot be in the past.", field_name="departure_time")

        if departure_time and arrival_time and arrival_time < departure_time:
            raise ValidationError("Arrival time must be after departure time.", field_name="arrival_time")

        # Validate route_id exists
        route_id = data.get("route_id")
        route = Route.query.get(route_id)
        if route_id and not route:
            raise ValidationError("Route with given ID does not exist.", field_name="route_id")
        
        # Validate departure/arrival  route is within the period
        if departure_time < route.period_start or departure_time > route.period_end:
            raise ValidationError("Departure times must be within the route period.", field_name="departure_time")
        if arrival_time > route.period_end or arrival_time > route.period_end:
            raise ValidationError("Arrival times must be within the route period.", field_name="arrival_time")
        
        # Validate aircraft_id exists
        aircraft_id = data.get("aircraft_id")
        if aircraft_id and not AirlineAircraft.query.get(aircraft_id):
            raise ValidationError("Airline aircraft with given ID does not exist.", field_name="aircraft_id")

class AirlineAircraftSchemaMinified(ma.SQLAlchemyAutoSchema):
    
    airline_id = ma.UUID(dump_only=True)
    
    aircraft = ma.Nested('app.schemas.aircraft.AircraftSchema', dump_only=True)
    class Meta:
        model = AirlineAircraft
        load_instance = False
        include_fk = True
        only = ('id', 'aircraft_id', 'airline_id','tail_number')


class AllFlightSchema(ma.SQLAlchemyAutoSchema):
    departure_airport = ma.Nested(AirportSchema, dump_only=True)
    arrival_airport = ma.Nested(AirportSchema, dump_only=True)
    flight_number = ma.String(dump_only=True)
    aircraft = ma.Nested(AirlineAircraftSchemaMinified, dump_only=True)
    route_id = ma.Integer(dump_only=True)
    is_editable = ma.Boolean(dump_only=True)

    @post_dump
    def add_is_editable(self, data, **kwargs):
        if 'id' in data:
            # Check if the route is associated with any flights
            flights_exist = db.session.query(
                exists().where(
                    or_(
                        BookingDepartureFlight.flight_id == data['id'],
                        BookingReturnFlight.flight_id == data['id']
                    )
            )).scalar()
            data['is_editable'] = not flights_exist
        return data

    class Meta:
        model = Flight
        load_instance = False
        include_fk = False
        exclude = ('checkin_start_time','checkin_end_time', 'boarding_start_time', 'boarding_end_time', 'gate', 'terminal', 'price_first_class', 'price_business_class', 'price_economy_class', 'price_insurance', )




class FlightExtraSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = FlightExtra
        load_instance = True
        include_fk = True        
    
    

    name = ma.String(attribute="extra.name",dump_only=True)
    description = ma.String(attribute="extra.description",dump_only=True)
    stackable = ma.Boolean(attribute="extra.stackable",dump_only=True)
    required_on_all_segments = ma.Boolean(attribute="extra.required_on_all_segments",dump_only=True)



flight_schema = FlightSchema()
flights_schema = FlightSchema(many=True)

all_flight_schema = AllFlightSchema()
all_flights_schema = AllFlightSchema(many=True)

flight_extra_schema = FlightExtraSchema()
flights_extra_schema = FlightExtraSchema(many=True)
