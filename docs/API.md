
### Authentication Endpoints (`/auth`)
These endpoints manage user authentication and registration. The authentication system uses a **JWT-based dual-token strategy** for security and a seamless user experience. Short-lived **access tokens (15-minute lifespan)** are stored in localStorage and sent via HTTP headers, while long-lived **refresh tokens (30-day lifespan)** are HTTP-only cookies to mitigate XSS attacks. A CSRF token is also used to prevent CSRF attacks. Automatic token refreshing is implemented, where a 401 error triggers a refresh request, and subsequent requests are queued and re-run with the new token.

*   **`POST /auth/login`**
    *   **Purpose**: Handles user login with email/password authentication.
    *   **Authentication**: None required.
    *   **Input**: JSON object containing `email` (string) and `password` (string).
    *   **Output**: JSON object with an `access_token` (string) and `user` object (containing `id`, `type`, and `active` status). The refresh token is set as an HTTP-only cookie.
    *   **Status Codes**:
        *   **200 OK**: Success.
        *   **401 Unauthorized**: Invalid credentials.
        *   **403 Forbidden**: User is not active.
        *   **500 Internal Server Error**.

*   **`POST /auth/register`**
    *   **Purpose**: Registers a new regular user.
    *   **Authentication**: None required.
    *   **Input**: JSON object containing `email`, `password`, `name`, `surname`, `address`, `zip`, and `nation_id`.
    *   **Output**: JSON object with an `access_token` (string) and `user` object (containing `id`, `type`, and `active` status).
    *   **Status Codes**:
        *   **200 OK**: Success.
        *   **400 Bad Request**: Validation error or user already exists.
        *   **500 Internal Server Error**.

*   **`POST /auth/refresh`**
    *   **Purpose**: Refreshes the access token using the refresh token cookie.
    *   **Authentication**: Refresh token cookie required.
    *   **Input**: None (uses HTTP-only cookie).
    *   **Output**: JSON object with a new `access_token` (string) and `user` object.
    *   **Status Codes**:
        *   **200 OK**: Success.
        *   **401 Unauthorized**: Invalid token.
        *   **403 Forbidden**: User is not active.
        *   **404 Not Found**: User not found.
        *   **500 Internal Server Error**.

*   **`POST /auth/logout`**
    *   **Purpose**: Logs out the user and clears the refresh token cookie.
    *   **Authentication**: None required.
    *   **Input**: None.
    *   **Output**: JSON object with a success `message`.
    *   **Status Codes**:
        *   **200 OK**: Success.

*   **`POST /auth/register_airline`**
    *   **Purpose**: Registers a new airline and creates an airline administrator user with a temporary password.
    *   **Authentication**: **Admin role required**.
    *   **Input**: JSON object containing `email`, `name`, `surname` of the admin, and `airline_name`.
    *   **Output**: JSON object with a success `message` and `credentials` (email and generated temporary `password`).
    *   **Status Codes**:
        *   **201 Created**: Airline registered successfully.
        *   **400 Bad Request**: User/airline already exists or validation error.
        *   **403 Forbidden**: Insufficient permissions (if not admin).
        *   **500 Internal Server Error**.

### Search Endpoints (`/search`)
These endpoints facilitate flight searches, including flexible date options, using the **RAPTOR algorithm** for efficient optimization. The RAPTOR algorithm operates by iteratively processing potential routes in rounds, starting from direct connections and systematically incorporating transfers to find optimal solutions. It is highly efficient and scalable, capable of managing extensive route datasets and complex networks.

*   **`GET /search/flights`**
    *   **Purpose**: Searches for flights using the RAPTOR algorithm.
    *   **Authentication**: Optional (affects data visibility regarding user's existing bookings).
    *   **Parameters**:
        *   `departure_airport_id` (integer) or `departure_city_id` (integer): Origin location ID.
        *   `departure_type` (string): Type of departure location (`"airport"` or `"city"`).
        *   `arrival_airport_id` (integer) or `arrival_city_id` (integer): Destination location ID.
        *   `arrival_type` (string): Type of arrival location (`"airport"` or `"city"`).
        *   `departure_date` (string): Date in DD-MM-YYYY format.
        *   `max_transfers` (integer, default: 3): Maximum number of connections.
        *   `limit` (integer, default: 10): Results per page.
        *   `page_number` (integer): Page number for pagination.
        *   `sort_by` (string): Sorting criteria (`price`, `duration`, `departure_time`). (Note: `order_by` in `search_doc.txt` is `price`, `duration`, `stops`).
        *   `class_type` (string): Preferred class (`ECONOMY_CLASS`, `BUSINESS_CLASS`, `FIRST_CLASS`). (Note: not explicitly in `search_doc.txt` for `GET /search/flights`, but pricing is by class)
        *   `airline_id` (string, optional): Filter by specific airline ID.
        *   `price_max` (float, optional): Maximum economy class price.
        *   `departure_time_min` (string, optional): Minimum departure time (HH:MM).
        *   `departure_time_max` (string, optional): Maximum departure time (HH:MM).
        *   `order_by_desc` (boolean, default: `False`): Order by field descending.
    *   **Output**: JSON object containing a list of `journeys` and `total_pages`. Each `journey` includes details like `flights` (segments), `total_duration`, `total_price` (economy, business, first class prices for the entire journey), `transfers` (number of stops), `is_direct` (boolean), `layovers` (list of layover airports and durations).
    *   **Status Codes**:
        *   **200 OK**: Success.
        *   **400 Bad Request**: Invalid date format or no valid airports found.

*   **`GET /search/flexible-dates`**
    *   **Purpose**: Gets minimum prices for each day in a month for a given departure and arrival location.
    *   **Authentication**: Optional.
    *   **Parameters**:
        *   Airport/city IDs (same as `/flights` for departure/arrival IDs and types).
        *   `departure_date` (string): Month in MM-YYYY format.
        *   `max_transfers` (integer, default: 3): Maximum number of connections.
        *   `airline_id` (string, optional): Filter by specific airline ID.
        *   `price_max` (float, optional): Maximum economy class price.
        *   `departure_time_min` (string, optional): Minimum departure time (HH:MM).
        *   `departure_time_max` (string, optional): Maximum departure time (HH:MM).
        *   `order_by` (string): Sorting criteria (`price`, `duration`, `stops`).
        *   `order_by_desc` (boolean, default: `False`): Order by field descending.
    *   **Output**: An array of objects, each containing a `date` and `min_price` for that day. If a date has no available flights, its price will be `null` or `None`.
    *   **Status Codes**:
        *   **200 OK**: Success.
        *   **400 Bad Request**: Invalid departure date format or no valid airports found.

### Flight Management Endpoints (`/flight`)
These endpoints provide detailed information about flights and their availability.

*   **`GET /flight/:flight_id`**
    *   **Purpose**: Gets detailed information for a specific flight.
    *   **Authentication**: Optional (affects data visibility).
    *   **Parameters**:
        *   `flight_id` (path): Flight UUID.
    *   **Output**: JSON object with `id`, `flight_number`, `departure_time`, `arrival_time`, `gate`, `terminal`, `aircraft` details, `route` details (departure/arrival airport), and `pricing` for each class (`first_class`, `business_class`, `economy_class`, `insurance`).
    *   **Status Codes**:
        *   **200 OK**: Success.
        *   **404 Not Found**: Flight not found.
        *   **500 Internal Server Error**.

*   **`GET /flight/seats/:flight_id`**
    *   **Purpose**: Gets seat availability for a specific flight.
    *   **Authentication**: None required.
    *   **Parameters**:
        *   `flight_id` (path): Flight UUID.
    *   **Output**: JSON object containing `seat_map` (showing available, occupied, and reserved seats by class), `aircraft_config` (rows, columns, unavailable seats), and `rows` (aircraft rows). Reserved seats include those in temporary `seat_session` and permanently booked seats.
    *   **Status Codes**:
        *   **200 OK**: Success.
        *   **404 Not Found**: Flight not found.
        *   **500 Internal Server Error**.

*   **`GET /flight/extra/:flight_id`**
    *   **Purpose**: Gets available extras for a specific flight.
    *   **Authentication**: None required.
    *   **Parameters**:
        *   `flight_id` (path): Flight UUID.
    *   **Output**: Array of `extra` objects, each with `id`, `name`, `description`, `price`, `limit`, `stackable`, and `required_on_all_segments`.
    *   **Status Codes**:
        *   **200 OK**: Success.
        *   **404 Not Found**: No extras found for the flight.
        *   **500 Internal Server Error**.

### Booking Endpoints (`/booking`)
These endpoints manage the complete flight booking process for users. During seat selection, a **temporary reservation session (seat_session) lasting 10 minutes** is activated to prevent concurrent bookings. If payment is successful, the seats are permanently booked; otherwise, they are released upon session expiration. A background scheduler cleans up expired sessions.

*   **`POST /booking`**
    *   **Purpose**: Creates a new booking with selected flights, extras, and optional insurance.
    *   **Authentication**: **User role required**.
    *   **Input**: JSON object containing:
        *   `session_id` (string): UUID of the active seat session.
        *   `departure_flights` (array of strings): List of departure flight IDs.
        *   `return_flights` (array of strings): List of return flight IDs.
        *   `extras` (array of objects): List of selected extras, each with `id` (string) and `quantity` (integer).
        *   `has_insurance` (boolean): Whether insurance was purchased.
        *   `payment_card_id` (integer). (Note: `booking_doc.txt` does not include `payment_card_id` in `BookingInput` model, suggesting it might be handled differently or implicitly.)
    *   **Output**: JSON object with `booking_id` (string), `booking_number` (string), `total_price` (float), and `payment_status` (`confirmed`).
    *   **Status Codes**:
        *   **201 Created**: Success.
        *   **400 Bad Request**: Validation errors or session expired.
        *   **403 Forbidden**: Seat session does not belong to the user, or extra does not belong to selected flights.
        *   **404 Not Found**: Flight or session not found.
        *   **409 Conflict**: Flight already booked.
        *   **500 Internal Server Error**.

*   **`GET /booking`**
    *   **Purpose**: Lists user bookings, filtered by role.
    *   **Authentication**: Required.
    *   **Parameters**:
        *   `flight_id` (query, optional): Filter by specific flight.
        *   `class_type` (query, optional): Filter by class type.
        *   `user_id` (query, optional): Filter by user (admin/airline-admin only).
        *   `limit` (query, optional): Results per page. (Note: not explicitly in `booking_doc.txt` for `GET /booking`.)
        *   `page_number` (query, optional): Page number for pagination. (Note: not explicitly in `booking_doc.txt` for `GET /booking`.)
    *   **Output**: Array of booking objects, each detailing `id`, `booking_number`, `departure_flights` (including flight details, seat, class, price, and extras), `return_flights`, `total_price`, `is_insurance_purchased`, and `insurance_price`.
    *   **Status Codes**:
        *   **200 OK**: Success.
        *   **400 Bad Request**: Airline ID required for airline-admin if filter applied.
        *   **403 Forbidden**: Insufficient permissions.
        *   **404 Not Found**.
        *   **500 Internal Server Error**.

*   **`GET /booking/:booking_id`**
    *   **Purpose**: Gets detailed information for a specific booking.
    *   **Authentication**: Required (owner, airline admin, or system admin).
    *   **Parameters**:
        *   `booking_id` (path): Booking UUID.
    *   **Output**: Detailed booking object (same format as list item).
    *   **Status Codes**:
        *   **200 OK**: Success.
        *   **403 Forbidden**: Insufficient permissions (not owner, admin, or airline admin for their airline's flight).
        *   **404 Not Found**: Booking not found.

*   **`DELETE /booking/:booking_id`**
    *   **Purpose**: Cancels/deletes a booking.
    *   **Authentication**: Required (booking owner or admin).
    *   **Parameters**:
        *   `booking_id` (path): Booking UUID.
    *   **Output**: JSON object with a success `message`.
    *   **Status Codes**:
        *   **200 OK**: Success.
        *   **403 Forbidden**: Insufficient permissions (not owner or admin).
        *   **404 Not Found**: Booking not found.
        *   **409 Conflict**: Cannot cancel due to existing dependencies.

### Location Endpoints (`/location`)
These endpoints provide data related to cities, airports, and nations for search interfaces.

*   **`GET /location/all`**
    *   **Purpose**: Gets all locations (cities, airports, nations) for search interfaces.
    *   **Authentication**: None required.
    *   **Parameters**:
        *   `search` (query, optional): Text search filter.
        *   `include_nations` (query, optional): Include nation data (boolean, default: `False`).
    *   **Output**: JSON object with a list of `cities`, each containing `id`, `name`, `nation` (if included, with `name` and `alpha2`), and `airports` (if included, with `id`, `name`, `iata_code`). The `location_model` output format indicates `id`, `name`, and `type` (`city`, `nation`, or `airport`).
    *   **Status Codes**:
        *   **200 OK**: Success.
        *   **500 Internal Server Error**.

*   **`GET /location/city`**
    *   **Purpose**: Searches cities with filtering.
    *   **Authentication**: None required.
    *   **Parameters**:
        *   `search` (query, optional): Text search filter (Note: in `list_parser` it's `name`).
        *   `nation_id` (query, optional): Filter by country ID.
        *   `limit` (query, optional): Results limit (Note: not explicitly in `location_doc.txt` for `GET /location/city`).
        *   `include_nation` (query, boolean, default: `False`): Include nation details in the output.
    *   **Output**: Array of city objects. Depending on `include_nation`, it can be `no_nation_city_model` or `city_model` including `nation` details.
    *   **Status Codes**:
        *   **200 OK**: Success.
        *   **500 Internal Server Error**.

*   **`GET /location/city/:city_id`**
    *   **Purpose**: Gets specific city details.
    *   **Authentication**: None required.
    *   **Parameters**:
        *   `city_id` (path): City ID.
    *   **Output**: City object with `id`, `name`, and `nation` (including `id`, `name`, `code`, `alpha2`).
    *   **Status Codes**:
        *   **200 OK**: Success.
        *   **404 Not Found**: City not found.
        *   **500 Internal Server Error**.

*   **`GET /location/nations`**
    *   **Purpose**: Gets a list of nations/countries with optional filtering.
    *   **Authentication**: None required.
    *   **Parameters**:
        *   `search` (query, optional): Text search filter (Note: in `nation_list_parser` it's `name`).
        *   `limit` (query, optional): Results limit (Note: not explicitly in `location_doc.txt` for `GET /location/nations`).
        *   `code` (query, optional): Filter by nation code (case-insensitive, partial match).
        *   `alpha2` (query, optional): Filter by nation alpha2 code (case-insensitive, exact match).
    *   **Output**: Array of nation objects, each with `id`, `name`, `code`, and `alpha2`.
    *   **Status Codes**:
        *   **200 OK**: Success.
        *   **500 Internal Server Error**.

*   **`GET /location/nation/:nation_id`**
    *   **Purpose**: Gets specific nation details.
    *   **Authentication**: None required.
    *   **Parameters**:
        *   `nation_id` (path): Nation ID.
    *   **Output**: Single nation object with `id`, `name`, `code`, and `alpha2`.
    *   **Status Codes**:
        *   **200 OK**: Success.
        *   **404 Not Found**: Nation not found.
        *   **500 Internal Server Error**.

### User Management Endpoints (`/user`)
These endpoints handle user profile management and payment information.

*   **`GET /user/me`**
    *   **Purpose**: Gets the current user's profile.
    *   **Authentication**: Required (any authenticated user).
    *   **Input**: None.
    *   **Output**: JSON object with `id`, `email`, `name`, `surname`, `address`, `zip`, `active` status, `type` (user or airline), `nation` details, and `payment_cards` list.
    *   **Status Codes**:
        *   **200 OK**: Success.
        *   **404 Not Found**: User not found.
        *   **500 Internal Server Error**.

*   **`GET /user/:user_id`**
    *   **Purpose**: Gets a user profile by ID.
    *   **Authentication**: Required (self or admin).
    *   **Parameters**:
        *   `user_id` (path): User UUID.
    *   **Output**: Same as `/user/me` but without payment cards, including `id`, `email`, `name`, `surname`, `address`, `zip`, `nation_id`, `airline_id`, and `active` status.
    *   **Status Codes**:
        *   **200 OK**: Success.
        *   **403 Forbidden**: Insufficient permissions (not self or admin).
        *   **404 Not Found**: User not found.

*   **`PUT /user/:user_id`**
    *   **Purpose**: Updates user information.
    *   **Authentication**: Required (self or admin).
    *   **Parameters**:
        *   `user_id` (path): User UUID.
    *   **Input**: JSON object with optional fields: `email`, `name`, `surname`, `address`, `zip`, `nation_id`. Admin users can also update `active` and `airline_id`.
    *   **Output**: Updated user object (same format as `GET /user/me` but without payment cards).
    *   **Status Codes**:
        *   **200 OK**: Success.
        *   **400 Bad Request**: Validation errors or email already exists.
        *   **403 Forbidden**: Insufficient permissions (not self or admin, or attempting to change restricted fields).
        *   **404 Not Found**: User not found.

*   **`POST /user/update_password`**
    *   **Purpose**: Updates the user's password.
    *   **Authentication**: Required (any authenticated user).
    *   **Input**: JSON object with `old_password` and `new_password`.
    *   **Output**: JSON object with a success `message`.
    *   **Status Codes**:
        *   **200 OK**: Success.
        *   **403 Forbidden**: Incorrect old password.
        *   **404 Not Found**: User or associated airline not found.
        *   **500 Internal Server Error**.

*   **`GET /user/cards`**
    *   **Purpose**: Gets the current user's payment cards.
    *   **Authentication**: Required (any authenticated user).
    *   **Input**: None.
    *   **Output**: Array of payment card objects, each with `id`, `card_name`, `holder_name`, `last_4_digits`, `expiration_date`, `circuit`, and `card_type` (`CREDIT`, `DEBIT`, `PREPAID`).
    *   **Status Codes**:
        *   **200 OK**: Success.
        *   **404 Not Found**: User not found.
        *   **500 Internal Server Error**.

*   **`POST /user/cards`**
    *   **Purpose**: Adds a new payment card for the current user.
    *   **Authentication**: Required (any authenticated user).
    *   **Input**: JSON object with `card_name`, `holder_name`, `last_4_digits`, `expiration_date`, `circuit`, and `card_type`.
    *   **Output**: Created payment card object.
    *   **Status Codes**:
        *   **201 Created**: Success.
        *   **400 Bad Request**: Validation error.

*   **`GET /user/cards/:card_id`**
    *   **Purpose**: Gets a specific payment card.
    *   **Authentication**: Required (card owner).
    *   **Parameters**:
        *   `card_id` (path): Payment card ID.
    *   **Output**: Payment card object.
    *   **Status Codes**:
        *   **200 OK**: Success.
        *   **404 Not Found**: Card not found.
        *   **500 Internal Server Error**.

*   **`DELETE /user/cards/:card_id`**
    *   **Purpose**: Deletes a payment card.
    *   **Authentication**: Required (card owner).
    *   **Parameters**:
        *   `card_id` (path): Payment card ID.
    *   **Output**: JSON object with a success `message`.
    *   **Status Codes**:
        *   **200 OK**: Success.
        *   **404 Not Found**: Card not found.
        *   **409 Conflict**: Card has dependencies.
        *   **500 Internal Server Error**.

### Airport Endpoints (`/airports`)
These endpoints provide information about airports.

*   **`GET /airports`**
    *   **Purpose**: Gets a list of airports with filtering options.
    *   **Authentication**: None required.
    *   **Parameters**:
        *   `search` (query, optional): Text search filter in airport names (Note: `name` in `list_parser`).
        *   `city_id` (query, optional): Filter by city ID (Note: `city_name` in `list_parser`).
        *   `limit` (query, optional): Number of results (default: 50). (Note: not explicitly in `airport_doc.txt` for `GET /airports`.)
        *   `nation_name` (query, optional): Filter by nation name (case-insensitive, partial match).
        *   `iata_code` (query, optional): Filter by IATA code (case-insensitive).
        *   `icao_code` (query, optional): Filter by ICAO code (case-insensitive).
    *   **Output**: Array of airport objects, each with `id`, `name`, `iata_code`, `icao_code`, `latitude`, `longitude`, and associated `city` (`id`, `name`, `nation`).
    *   **Status Codes**:
        *   **200 OK**: Success.
        *   **500 Internal Server Error**.

*   **`GET /airports/:airport_id`**
    *   **Purpose**: Gets specific airport details.
    *   **Authentication**: None required.
    *   **Parameters**:
        *   `airport_id` (path): Airport ID.
    *   **Output**: Single airport object (same format as list).
    *   **Status Codes**:
        *   **200 OK**: Success.
        *   **404 Not Found**: Airport not found.
        *   **500 Internal Server Error**.

### Aircraft Endpoints (`/aircraft`)
These endpoints provide details about aircraft models.

*   **`GET /aircraft`**
    *   **Purpose**: Gets a list of aircraft types.
    *   **Authentication**: None required.
    *   **Input**: None.
    *   **Output**: Array of aircraft objects, each with `id`, `name`, `rows`, `columns`, and `unavailable_seats`.
    *   **Status Codes**:
        *   **200 OK**: Success.
        *   **500 Internal Server Error**.

*   **`GET /aircraft/:aircraft_id`**
    *   **Purpose**: Gets specific aircraft details.
    *   **Authentication**: None required.
    *   **Parameters**:
        *   `aircraft_id` (path): Aircraft ID.
    *   **Output**: Single aircraft object.
    *   **Status Codes**:
        *   **200 OK**: Success.
        *   **404 Not Found**: Aircraft not found.
        *   **500 Internal Server Error**.

### Seat Session Management Endpoints (`/seat_session`)
These endpoints manage temporary seat reservations during the booking process.

*   **`GET /seat_session`**
    *   **Purpose**: Gets the current user's active seat session.
    *   **Authentication**: **User role required**.
    *   **Input**: None.
    *   **Output**: JSON object with `id`, `user_id`, `seats` (list of seat objects with `flight_id`, `seat_number`, `class_type`), `session_start_time`, and `session_end_time`.
    *   **Status Codes**:
        *   **200 OK**: Success.
        *   **404 Not Found**: No active session for the user.

*   **`POST /seat_session`**
    *   **Purpose**: Creates a new seat session (replaces any existing one for the user).
    *   **Authentication**: **User role required**.
    *   **Input**: None.
    *   **Output**: New seat session object.
    *   **Status Codes**:
        *   **201 Created**: Success.
        *   **409 Conflict**: (Documentation states "You already have an active session" but code shows it deletes and creates a new one).
        *   **404 Not Found**: (Documentation error, should be 201 created if success).

*   **`GET /seat_session/:session_id`**
    *   **Purpose**: Gets specific seat session details.
    *   **Authentication**: Required (session owner).
    *   **Parameters**:
        *   `session_id` (path): Session UUID.
    *   **Output**: Seat session object.
    *   **Status Codes**:
        *   **200 OK**: Success.
        *   **400 Bad Request**: Session not found.
        *   **403 Forbidden**: Not session owner.

*   **`POST /seat_session/:session_id`**
    *   **Purpose**: Adds a seat to a session.
    *   **Authentication**: Required (session owner).
    *   **Parameters**:
        *   `session_id` (path): Session UUID.
    *   **Input**: JSON object with `flight_id` (string) and `seat_number` (string).
    *   **Output**: JSON object with `message` "Ok" and `code` 201.
    *   **Status Codes**:
        *   **201 Created**: Seat added successfully.
        *   **400 Bad Request**: Session expired.
        *   **403 Forbidden**: Not session owner.
        *   **404 Not Found**: Flight or seat not found in aircraft.
        *   **409 Conflict**: Seat unavailable (already in use or selected).

*   **`DELETE /seat_session/:session_id`**
    *   **Purpose**: Deletes a seat session and releases all seats.
    *   **Authentication**: Required (session owner).
    *   **Parameters**:
        *   `session_id` (path): Session UUID.
    *   **Output**: JSON object with a success `message` and `code` 200.
    *   **Status Codes**:
        *   **200 OK**: Success.
        *   **400 Bad Request**: Session not found.
        *   **403 Forbidden**: Not session owner.

### Airline Management Endpoints (`/airline`)
These endpoints provide functionalities for airline administrators to manage their airline's profile, aircrafts, routes, flights, and extra services. This includes managing seat layouts for each aircraft.

*   **`GET /airline/all`**
    *   **Purpose**: Gets a list of all airlines (publicly accessible).
    *   **Authentication**: None required.
    *   **Input**: None.
    *   **Parameters**:
        *   `name` (query, optional): Filter by airline name (case-insensitive).
        *   `nation_id` (query, optional): Filter by nation ID.
    *   **Output**: Array of airline objects, each with `id`, `name`, and `nation` (`name`, `alpha2`).
    *   **Status Codes**:
        *   **200 OK**: Success.
        *   **400 Bad Request**.
        *   **500 Internal Server Error**.

*   **`GET /airline`**
    *   **Purpose**: Gets the current airline details for the authenticated airline administrator.
    *   **Authentication**: **Airline-admin role required**.
    *   **Input**: None.
    *   **Output**: Complete airline object with all details (e.g., `id`, `name`, `address`, `zip`, `nation`, `email`, `website`, class descriptions, `extras` list).
    *   **Status Codes**:
        *   **200 OK**: Success.
        *   **403 Forbidden**: Unauthorized.
        *   **404 Not Found**: Airline not found.

*   **`PUT /airline/:airline_id`**
    *   **Purpose**: Updates airline information.
    *   **Authentication**: **Airline-admin role required** (for their own airline).
    *   **Parameters**:
        *   `airline_id` (path): Airline UUID.
    *   **Input**: JSON object with optional fields: `name`, `nation_id`, `address`, `zip`, `email`, `website`, `first_class_description`, `business_class_description`, `economy_class_description`.
    *   **Output**: Updated airline object.
    *   **Status Codes**:
        *   **200 OK**: Success.
        *   **400 Bad Request**: Validation errors.
        *   **403 Forbidden**: Insufficient permissions (not owner).
        *   **404 Not Found**: Airline not found.

*   **`GET /airline/:airline_id`**
    *   **Purpose**: Gets specific airline details (publicly accessible).
    *   **Authentication**: None required.
    *   **Parameters**:
        *   `airline_id` (path): Airline UUID.
    *   **Output**: Public airline information object (includes `nation` and `extras`).
    *   **Status Codes**:
        *   **200 OK**: Success.
        *   **404 Not Found**: Airline not found.

*   **`GET /airline/aircrafts`**
    *   **Purpose**: Gets an airline's aircraft fleet.
    *   **Authentication**: **Airline-admin role required**.
    *   **Input**: None.
    *   **Output**: Array of aircraft objects, each with `id`, `tail_number`, and `aircraft` details (`name`, `rows`, `columns`, `unavailable_seats`).
    *   **Status Codes**:
        *   **200 OK**: Success.
        *   **403 Unauthorized**.
        *   **404 Not Found**.

*   **`POST /airline/aircrafts`**
    *   **Purpose**: Adds an aircraft to the airline fleet.
    *   **Authentication**: **Airline-admin role required**.
    *   **Input**: JSON object with `aircraft_id` (integer), `tail_number` (string), and optional lists for `first_class_seats`, `business_class_seats`, and `economy_class_seats` (array of strings).
    *   **Output**: Created aircraft object.
    *   **Status Codes**:
        *   **201 Created**: Success.
        *   **400 Bad Request**.
        *   **403 Forbidden**: Unauthorized (e.g., aircraft does not belong to airline).
        *   **404 Not Found**.
        *   **409 Conflict**: (e.g., duplicate tail number).
        *   **500 Internal Server Error**.

*   **`GET /airline/aircrafts/:aircraft_id`**
    *   **Purpose**: Gets specific aircraft details for an airline.
    *   **Authentication**: **Airline-admin role required**.
    *   **Parameters**:
        *   `aircraft_id` (path): Airline Aircraft UUID.
    *   **Output**: Detailed aircraft object.
    *   **Status Codes**:
        *   **200 OK**: Success.
        *   **403 Forbidden**: Not authorized (aircraft does not belong to airline).
        *   **404 Not Found**: Aircraft not found.

*   **`PUT /airline/aircrafts/:aircraft_id`**
    *   **Purpose**: Updates aircraft configuration.
    *   **Authentication**: **Airline-admin role required**.
    *   **Parameters**:
        *   `aircraft_id` (path): Airline Aircraft UUID.
    *   **Input**: Aircraft update data (optional fields: `aircraft_id`, `first_class_seats`, `business_class_seats`, `economy_class_seats`, `tail_number`).
    *   **Output**: Updated aircraft object.
    *   **Status Codes**:
        *   **200 OK**: Success.
        *   **400 Bad Request**.
        *   **403 Forbidden**: Not authorized (aircraft does not belong to airline).
        *   **404 Not Found**: Aircraft not found.

*   **`DELETE /airline/aircrafts/:aircraft_id`**
    *   **Purpose**: Removes an aircraft from the fleet.
    *   **Authentication**: **Airline-admin role required**.
    *   **Parameters**:
        *   `aircraft_id` (path): Airline Aircraft UUID.
    *   **Output**: JSON object with a success `message`.
    *   **Status Codes**:
        *   **200 OK**: Success.
        *   **403 Forbidden**: Not authorized (aircraft does not belong to airline).
        *   **404 Not Found**: Aircraft not found.
        *   **409 Conflict**: Aircraft has dependencies (associated with flights).

*   **`GET /airline/routes`**
    *   **Purpose**: Gets an airline's routes.
    *   **Authentication**: **Airline-admin role required**.
    *   **Input**: None.
    *   **Output**: Array of route objects with airport details (e.g., `id`, `flight_number`, `departure_airport`, `arrival_airport`, `period_start`, `period_end`, `is_editable`).
    *   **Status Codes**:
        *   **200 OK**: Success.
        *   **404 Not Found**.

*   **`POST /airline/routes`**
    *   **Purpose**: Creates a new route.
    *   **Authentication**: **Airline-admin role required**.
    *   **Input**: JSON object with `flight_number`, `departure_airport_id`, `arrival_airport_id`, `period_start`, and `period_end`.
    *   **Output**: Created route object.
    *   **Status Codes**:
        *   **201 Created**: Success.
        *   **400 Bad Request**: Validation error.
        *   **403 Unauthorized**.

*   **`GET /airline/routes/:route_id`**
    *   **Purpose**: Gets specific route details.
    *   **Authentication**: **Airline-admin role required**.
    *   **Parameters**:
        *   `route_id` (path): Route ID.
    *   **Output**: Detailed route object.
    *   **Status Codes**:
        *   **200 OK**: Success.
        *   **403 Unauthorized**: Not authorized (route does not belong to airline).
        *   **404 Not Found**: Route not found.

*   **`PUT /airline/routes/:route_id`**
    *   **Purpose**: Updates route information.
    *   **Authentication**: **Airline-admin role required**.
    *   **Parameters**:
        *   `route_id` (path): Route ID.
    *   **Input**: Route update data (optional fields: `departure_airport_id`, `arrival_airport_id`, `period_start`, `period_end`, `flight_number`).
    *   **Output**: Updated route object.
    *   **Status Codes**:
        *   **200 OK**: Success.
        *   **400 Bad Request**: Validation error.
        *   **403 Unauthorized**: Not authorized (route does not belong to airline).
        *   **404 Not Found**: Route not found.

*   **`DELETE /airline/routes/:route_id`**
    *   **Purpose**: Deletes a route.
    *   **Authentication**: **Airline-admin role required**.
    *   **Parameters**:
        *   `route_id` (path): Route ID.
    *   **Output**: JSON object with a success `message`.
    *   **Status Codes**:
        *   **200 OK**: Success.
        *   **400 Bad Request**.
        *   **403 Forbidden**: Insufficient permissions (not owner).
        *   **404 Not Found**: Route not found.
        *   **409 Conflict**: Route has dependencies (associated flights).
        *   **500 Internal Server Error**.

*   **`GET /airline/flights`**
    *   **Purpose**: Gets an airline's flights with pagination.
    *   **Authentication**: **Airline-admin role required**.
    *   **Parameters**:
        *   `route_id` (query, optional): Filter by route (Note: not explicitly in `airline_doc.txt` for `GET /airline/flights`).
        *   `date_from` (query, optional): Filter from date (Note: not explicitly in `airline_doc.txt` for `GET /airline/flights`).
        *   `date_to` (query, optional): Filter to date (Note: not explicitly in `airline_doc.txt` for `GET /airline/flights`).
        *   `page_number` (integer, default: 1): Page number for pagination.
        *   `limit` (integer, default: 10): Results per page.
    *   **Output**: JSON object with `items` (array of flight objects) and `total_pages`. Each flight object includes `id`, `flight_number`, `aircraft` (minified), `route_id`, `departure_time`, `arrival_time`, `departure_airport`, `arrival_airport`.
    *   **Status Codes**:
        *   **200 OK**: Success.
        *   **400 Bad Request**: Page number or limit must be greater than 0.
        *   **404 Not Found**.

*   **`POST /airline/flights`**
    *   **Purpose**: Schedules a new flight.
    *   **Authentication**: **Airline-admin role required**.
    *   **Input**: JSON object with `route_id` (integer), `aircraft_id` (string UUID), `departure_time` (datetime), `arrival_time` (datetime), `price_economy_class`, `price_business_class`, `price_first_class` (floats), and optional `price_insurance` (float, default 0.0). Can also include `extras` (list of objects with `extra_id`, `price`, `limit`).
    *   **Output**: Created flight object (detailed output model).
    *   **Status Codes**:
        *   **201 Created**: Success.
        *   **400 Bad Request**: Validation error, including invalid flight times (e.g., departure in past, arrival before departure).
        *   **403 Forbidden**: The specified aircraft or extra does not belong to your airline.
        *   **409 Conflict**: Integrity error (e.g., duplicate flight number or route).

*   **`GET /airline/flights/:flight_id`**
    *   **Purpose**: Gets specific flight details, including booked seats.
    *   **Authentication**: **Airline-admin role required**.
    *   **Parameters**:
        *   `flight_id` (path): Flight UUID.
    *   **Output**: Detailed flight object, including `id`, `flight_number`, `aircraft` (full details), `route_id`, `departure_time`, `arrival_time`, `departure_airport`, `arrival_airport`, pricing details, gate, terminal, check-in/boarding times, `is_editable`, and `booked_seats` (list of seat numbers).
    *   **Status Codes**:
        *   **200 OK**: Success.
        *   **403 Forbidden**: Insufficient permissions (flight does not belong to airline).
        *   **404 Not Found**: Flight not found.

*   **`PUT /airline/flights/:flight_id`**
    *   **Purpose**: Updates flight information.
    *   **Authentication**: **Airline-admin role required**.
    *   **Parameters**:
        *   `flight_id` (path): Flight UUID.
    *   **Input**: Flight update data (similar to `POST /airline/flights` but all fields are optional, `airline_id` cannot be changed). Can include `extras` list to replace existing ones.
    *   **Output**: Updated flight object.
    *   **Status Codes**:
        *   **200 OK**: Success.
        *   **400 Bad Request**: Validation errors.
        *   **403 Forbidden**: Insufficient permissions (flight does not belong to airline, or extra does not belong to airline).
        *   **404 Not Found**: Flight not found.
        *   **409 Conflict**: Integrity error (e.g., duplicate flight number or route).

*   **`DELETE /airline/flights/:flight_id`**
    *   **Purpose**: Cancels/deletes a flight.
    *   **Authentication**: **Airline-admin role required**.
    *   **Parameters**:
        *   `flight_id` (path): Flight UUID.
    *   **Output**: JSON object with a success `message`.
    *   **Status Codes**:
        *   **200 OK**: Success.
        *   **400 Bad Request**.
        *   **403 Forbidden**: Insufficient permissions (flight does not belong to airline).
        *   **404 Not Found**: Flight not found.
        *   **409 Conflict**: Flight has bookings or has already departed.

*   **`GET /airline/extras`**
    *   **Purpose**: Gets an airline's extra services.
    *   **Authentication**: **Airline-admin role required**.
    *   **Input**: None.
    *   **Output**: Array of extra service objects, each with `id`, `name`, `description`, `airline_id`, `required_on_all_segments`, and `stackable`.
    *   **Status Codes**:
        *   **200 OK**: Success.
        *   **403 Unauthorized**.
        *   **404 Not Found**.

*   **`POST /airline/extras`**
    *   **Purpose**: Creates a new extra service for the airline. Note: Price is set per flight, not here.
    *   **Authentication**: **Airline-admin role required**.
    *   **Input**: JSON object with `name`, `description`, `required_on_all_segments` (boolean), and `stackable` (boolean).
    *   **Output**: Created extra service object.
    *   **Status Codes**:
        *   **201 Created**: Success.
        *   **400 Bad Request**: Validation error.
        *   **403 Unauthorized**.

*   **`GET /airline/extras/:extra_id`**
    *   **Purpose**: Gets specific extra service details.
    *   **Authentication**: **Airline-admin role required**.
    *   **Parameters**:
        *   `extra_id` (path): Extra UUID.
    *   **Output**: Extra service object.
    *   **Status Codes**:
        *   **200 OK**: Success.
        *   **403 Unauthorized**: Not authorized (extra does not belong to airline).
        *   **404 Not Found**: Extra not found.

*   **`PUT /airline/extras/:extra_id`**
    *   **Purpose**: Updates an extra service.
    *   **Authentication**: **Airline-admin role required**.
    *   **Parameters**:
        *   `extra_id` (path): Extra UUID.
    *   **Input**: Extra service update data (optional fields: `name`, `description`, `required_on_all_segments`, `stackable`).
    *   **Output**: Updated extra service object.
    *   **Status Codes**:
        *   **200 OK**: Success.
        *   **400 Bad Request**: Validation error.
        *   **403 Unauthorized**: Not authorized (extra does not belong to airline).
        *   **404 Not Found**: Extra not found.

*   **`DELETE /airline/extras/:extra_id`**
    *   **Purpose**: Deletes an extra service.
    *   **Authentication**: **Airline-admin role required**.
    *   **Parameters**:
        *   `extra_id` (path): Extra UUID.
    *   **Output**: JSON object with a success `message`.
    *   **Status Codes**:
        *   **200 OK**: Success.
        *   **403 Unauthorized**: Not authorized (extra does not belong to airline).
        *   **404 Not Found**: Extra not found.
        *   **409 Conflict**: Extra has dependencies (associated with flights).

*   **`GET /airline/stats`**
    *   **Purpose**: Gets airline statistics and analytics. These statistics are saved to a Redis cache and recalculated regularly by a background scheduler to optimize performance.
    *   **Authentication**: **Airline-admin role required**.
    *   **Input**: None.
    *   **Output**: JSON object with `total_flights`, `total_bookings`, `revenue`, `occupancy_rate`, `popular_routes`, `flights_fullfilment`, `mostRequestedRoutes`, `airportsWithMostFlights`, and `leastUsedRoute`.
    *   **Status Codes**:
        *   **200 OK**: Success.
        *   **500 Internal Server Error**.

### Admin Panel Endpoints (`/admin`)
These endpoints are reserved for system administrators to manage users and airlines.

*   **`GET /admin/users`**
    *   **Purpose**: Lists all users with optional filtering.
    *   **Authentication**: **Admin role required**.
    *   **Parameters**:
        *   `search` (query, optional): Search by email/name (Note: `email` and `name` in `user_list_parser`).
        *   `role` (query, optional): Filter by role.
        *   `active` (query, optional): Filter by active status (boolean).
    *   **Output**: Array of user objects, including `id`, `email`, `name`, `surname`, `address`, `zip`, `nation`, `airline_id`, `active`, and `type`.
    *   **Status Codes**:
        *   **200 OK**: Success.
        *   **403 Forbidden**: Insufficient permissions.
        *   **500 Internal Server Error**.

*   **`DELETE /admin/users/:user_id`**
    *   **Purpose**: Deletes a user account.
    *   **Authentication**: **Admin role required**.
    *   **Parameters**:
        *   `user_id` (path): User UUID.
    *   **Output**: JSON object with a success `message`.
    *   **Status Codes**:
        *   **200 OK**: Success.
        *   **404 Not Found**: User not found.
        *   **409 Conflict**: User has dependencies (cannot delete last admin user, or user has an associated airline).

*   **`GET /admin/airlines`**
    *   **Purpose**: Lists all airlines (admin only).
    *   **Authentication**: **Admin role required**.
    *   **Input**: None.
    *   **Output**: Array of airline objects with details, including `id`, `name`, `nation`, `address`, `zip`, `email`, `website`, class descriptions, and an associated `user` (airline admin).
    *   **Status Codes**:
        *   **200 OK**: Success.
        *   **403 Forbidden**: Insufficient permissions.
        *   **500 Internal Server Error**.

*   **`PUT /admin/airlines/:airline_id`**
    *   **Purpose**: Updates airline information (admin only).
    *   **Authentication**: **Admin role required**.
    *   **Parameters**:
        *   `airline_id` (path): Airline UUID.
    *   **Input**: Airline update data (optional fields: `name`, `address`, `zip`, `nation_id`, `email`, `website`, class descriptions).
    *   **Output**: Updated airline object.
    *   **Status Codes**:
        *   **200 OK**: Success.
        *   **400 Bad Request**: Validation error.
        *   **404 Not Found**: Airline not found.

*   **`DELETE /admin/airlines/:airline_id`**
    *   **Purpose**: Deletes an airline and all associated users.
    *   **Authentication**: **Admin role required**.
    *   **Parameters**:
        *   `airline_id` (path): Airline UUID.
    *   **Output**: JSON object with a success `message`.
    *   **Status Codes**:
        *   **200 OK**: Success.
        *   **404 Not Found**: Airline not found.
        *   **409 Conflict**: Airline has dependencies.