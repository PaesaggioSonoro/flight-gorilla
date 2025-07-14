# System Architecture – FlightGorilla

**FlightGorilla** is a scalable full-stack web application designed for modern flight booking and airline management. This document outlines the architectural structure, component relationships, technology stack, and implementation strategies.

---

## High-Level Architecture

FlightGorilla is structured across three primary layers:

### 1. Frontend Layer
- Built with Angular 19 (Single Page Application)
- Styled using Tailwind CSS and Spartan UI
- Visualization powered by Chart.js for interactive airline analytics

### 2. Backend Layer
- Two interchangeable implementations:
  - **Python + Flask**: REST API built using Flask-RESTX, SQLAlchemy ORM, and Marshmallow for serialization and validation
  - **Node.js + Express**: Developed in TypeScript with Prisma ORM and Zod for schema validation
- Both versions expose RESTful APIs and integrate Swagger/OpenAPI documentation

### 3. Data Layer
- **PostgreSQL** as the relational database
- **Redis** for caching and managing concurrency-sensitive operations (e.g., seat sessions)
- Background task scheduling via Redis queues for statistical aggregation and cleanup jobs

---

## Component Communication

- The Angular frontend communicates with the backend using HTTP REST APIs.
- The backend manages business logic, user authentication, and request validation.
- PostgreSQL stores core entities such as users, flights, bookings, aircraft configurations, and extras.
- Redis is used for caching expensive computations and maintaining temporary booking state.

---

## Backend Capabilities

- **Flexible Location-Based Search**: Users can search by city or specific airport, with the system automatically grouping results.
- **Flexible Date Range Support**: Users can query an entire month to identify the lowest-priced dates.
- **Multi-Leg Flight Search**: Supports complex itineraries with multiple transfers using the RAPTOR algorithm.
- **Seat Session Management**: Implements temporary seat holds to avoid race conditions in the booking process.
- **Custom Seat Layouts**: Airlines can assign different seat classes within immutable aircraft models.
- **Extras System**: Airlines can define optional flight-specific services such as baggage, meals, or insurance.
- **Admin Interfaces**: Airline dashboards present real-time revenue, route demand, and booking metrics.
- **Secure Authentication**: Dual-token JWT strategy with access and refresh tokens, CSRF protection, and role-based authorization.

---

## Deployment and Containerization

- All components are containerized using Docker for reproducibility and isolated development.
- Multi-stage Docker builds minimize image size and optimize CI/CD pipelines.
- Development environments are managed via `docker-compose.yaml` (Python) and `docker-compose-ts.yml` (Node.js).
- Health checks and service readiness ensure stable orchestration and monitoring.

---

## RAPTOR Algorithm for Flight Search

FlightGorilla implements the RAPTOR (Round-Based Public Transit Routing) algorithm to efficiently evaluate direct and multi-stop itineraries:

- Iterative rounds compute increasingly complex paths
- Fast computation without reliance on graph structures
- Excellent scalability for complex routing scenarios, including flexible date searches

---

## API Validation and Documentation

- **Python Backend**:
  - Data validation and serialization via Marshmallow
  - API structure and documentation via Flask-RESTX

- **Node.js Backend**:
  - Schema validation using Zod
  - RESTful API documentation with OpenAPI (Swagger)

---

## Database Design and Optimization

- Relational schema optimized with strategic indexing:
  - pg_trgm indexes for text search on cities, nations, and airports
  - Composite and foreign key indexes for efficient joins and flight lookups
- Custom triggers enforce integrity:
  - Prevent seat overbooking
  - Validate extra limits and seat class assignments
- Development metrics tracked with `pg_stat_statements` and `pg_stat_user_tables`

---

## Analytics and Caching

- Airline dashboards aggregate:
  - Monthly and total revenue
  - Flight occupancy rates
  - High- and low-performing routes
- All analytics are cached in Redis and refreshed on a scheduled interval via background workers

---

## Role-Based Access Control

Access throughout the platform is governed by a multi-tier role system:

- **Passenger**: Flight search and booking
- **Airline Administrator**: Aircraft, route, and flight management, analytics dashboard
- **System Administrator**: Full control over user and airline data

Frontend route guards and backend middleware enforce access policies, while token-based session persistence ensures seamless navigation after login or token refresh.

---

## Related Documentation

- [Project Overview (README)](../README.md)
