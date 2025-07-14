# ✈️ FlightGorilla

**Full-stack flight booking platform with flexible search, airline admin tools, and real-time seat management.**

---

## 🧭 Overview

FlightGorilla is an advanced web application designed to simulate a modern, large-scale airline booking platform. It empowers users to search and book flights based on their preferences, including flexible date ranges and multi-stop itineraries, while enabling airlines to manage their operations, aircraft, routes, and pricing dynamically.

Unlike basic booking apps, FlightGorilla integrates a flexible location model (city or airport), advanced date search (month-wide), and supports real-time concurrency-safe seat reservations using a seat session model. It also handles extras (like baggage or meals), pricing logic, aircraft layout customization, airline analytics, and a full role-based permission system.

The system is built as a full-stack solution with both Python (Flask) and Node.js (Express) backend implementations, making it ideal for educational use, scalable deployments, or enterprise prototyping. The architecture supports containerization, RESTful APIs, and modular design with strict separation of concerns.


---

## 🔧 Architecture

The system is composed of three layers:

- **Frontend**: Angular 19
- **Backend**:
  - Python + Flask (REST API with Marshmallow, Flask-RESTX)
  - Node.js + Express (TypeScript + Prisma ORM)
- **Database**: PostgreSQL with Redis caching

Both backends support a modular, containerized architecture using Docker.

---

## 🚀 Features

- 🔍 **Flexible location & date search** (city or airport, full-month pricing)
- 🛫 **Multi-leg flights** with unlimited transfers (RAPTOR algorithm)
- 💺 **Custom aircraft seat layouts** per airline
- ⏱️ **Seat sessions** to prevent double booking
- 📦 **Extras** like baggage, WiFi, meals – configurable per flight
- 🧾 **Interactive API docs** via Swagger/OpenAPI
- 🔐 **JWT authentication** with refresh tokens & CSRF protection
- 🧠 **Smart caching** of stats with Redis
- 📊 **Admin dashboards** with charts and performance insights

---

## 📁 Project Structure

```plaintext
FlightGorilla/
├── backend-py/               # Python (Flask) backend
│   ├── app/
│   │   ├── apis/             # REST endpoints (Flask-RESTX)
│   │   ├── commands/         # CLI scripts for seeding data
│   │   ├── core/             # Auth, stats, background logic
│   │   ├── main/             # Entry routing
│   │   ├── models/           # SQLAlchemy models
│   │   └── schemas/          # Marshmallow schemas
│   ├── init/                 # SQL scripts
│   ├── migrations/           # Alembic migrations
│   ├── requirements.txt      # Python dependencies
│   ├── Dockerfile            # Docker build config
│   └── docker-compose.yaml   # Docker dev environment
│
├── backend-ts/               # Node.js (Express + TypeScript) backend
│   ├── generated/            # Prisma client
│   ├── package.json          # Node dependencies
│   ├── tsconfig.json         # TS config
│   ├── Dockerfile            # Docker build config
│   └── README.md             # TS backend documentation
│
├── docker-compose-ts.yml     # Docker Compose for TS backend
└── .gitignore
