# SmartHotel Management System - Legacy Monolith
## *A Deliberately Poor Architecture for Modernization Training*

---

## ⚠️ WARNING: THIS IS INTENTIONALLY POORLY DESIGNED

This application is a training tool to demonstrate bad architectural practices and technical debt. **Do NOT use this as a reference for production code.**

---

## Quick Start

### Installation

```bash
# Navigate to the project directory
cd SmartHotel

# Install dependencies
pip install flask

# Run the application
python app.py
```

The application will start on **http://localhost:5000**

### Demo Credentials
- **Username:** `admin`
- **Password:** `admin123`

---

## Project Structure

```
SmartHotel/
├── app.py                    # MONOLITH: Everything in one file
├── static/
│   └── style.css            # Basic CSS (no frontend framework)
├── templates/
│   ├── base.html            # Layout template
│   ├── login.html           # Login page
│   ├── index.html           # Hotel dashboard
│   ├── hotel_detail.html    # Hotel details
│   ├── rooms.html           # Room list
│   ├── add_room.html        # Add room form
│   ├── edit_room.html       # Edit room form
│   ├── bookings.html        # Booking list
│   ├── add_booking.html     # Create booking form
│   ├── customers.html       # Customer list
│   ├── add_customer.html    # Add customer form
│   └── search_results.html  # Search results
├── hotel.db                 # SQLite database (auto-created)
└── README.md               # This file
```

---

## Features Implemented

### 1. **Hotel Dashboard**
   - Lists all hotels
   - Displays basic info (name, location, rating)
   - No filtering or sorting

### 2. **Room Management**
   - Add new rooms
   - View all rooms (no pagination)
   - Edit room details
   - Delete rooms

### 3. **Booking System**
   - Book a room (name, date, duration)
   - View all bookings (no pagination)
   - Cancel bookings
   - **NO date conflict prevention**

### 4. **Customer Management**
   - Add customers
   - View all customers (no pagination)
   - **NO duplicate email checking**

### 5. **Basic Search**
   - Search hotels by name/location
   - Search rooms by number/type
   - Search customers by name/email
   - **NO result limited or pagination**

### 6. **Authentication**
   - Simple login system
   - **Plain text passwords** (INSECURE)
   - Session-based authentication
   - **NO CSRF protection**

---

## 🚨 Intentional Anti-Patterns (MANDATORY for Training)

### Architecture & Design
- ❌ **Everything in `app.py`** - No modularization
- ❌ **Business logic mixed with routes** - No separation of concerns
- ❌ **No abstraction layers** - Raw SQL everywhere
- ❌ **Tight coupling** - UI tightly coupled to backend
- ❌ **Duplicate code** - Same logic repeated across routes
- ❌ **No API layer** - HTML forms directly tied to backend logic

### Database & Data
- ❌ **Raw SQL queries** - No ORM or query builder
- ❌ **Hardcoded database path** - `DATABASE = "hotel.db"`
- ❌ **No migrations** - Schema created inline during init
- ❌ **No validation** - Weak or missing input validation
- ❌ **No transactions** - Multi-step operations not atomic
- ❌ **No pagination** - All records loaded at once

### Security
- ❌ **Plain text passwords** - Stored in plaintext
- ❌ **No password hashing** - `password == input`
- ❌ **No CSRF protection** - No token validation
- ❌ **Hardcoded secret key** - `"hardcoded_insecure_key_12345"`
- ❌ **No encryption** - Sensitive data exposed
- ❌ **No rate limiting** - Brute force attacks possible
- ❌ **No SQL injection protection** (mostly using parameters but with vulnerabilities)

### Configuration & Deployment
- ❌ **No environment variables** - Hardcoded config
- ❌ **Debug mode always enabled** - `app.debug = True`
- ❌ **Host bound to 0.0.0.0** - Exposed to network
- ❌ **No Docker** - No containerization
- ❌ **No CI/CD** - No automated deployment
- ❌ **No requirements.txt** - Dependencies not documented

### Error Handling & Logging
- ❌ **Using `print()` for logging** - No logging framework
- ❌ **No structured logging** - Inconsistent error messages
- ❌ **Bare `except` clauses** - Catches all exceptions
- ❌ **Logging sensitive data** - Passwords, emails logged
- ❌ **No error tracking** - No alerting or monitoring
- ❌ **Poor error messages** - Generic "Error loading X" messages

### Testing & Quality
- ❌ **No unit tests** - Zero test coverage
- ❌ **No integration tests** - Untested workflows
- ❌ **No linting** - Code style not enforced
- ❌ **No type hints** - Dynamic typing everywhere
- ❌ **No documentation** - Code comments missing
- ❌ **No code review process** - No quality gates

### User Experience
- ❌ **No pagination** - Loads hundreds of records
- ❌ **No filtering/sorting** - Tables show all data unsorted
- ❌ **Minimal UI** - Bootstrap not even used
- ❌ **No form validation** - client-side or server-side
- ❌ **Poor UX** - No loading indicators, confirmations, etc.
- ❌ **Not responsive** - No mobile support

### Other Issues
- ❌ **Global database connection** - Shared across threads
- ❌ **No dependency injection** - Everything hardcoded
- ❌ **No versioning** - No API versioning
- ❌ **No documentation** - Architecture not documented
- ❌ **Hardcoded sample data** - Test data in production code

---

## Database Schema

### Tables
1. **hotels** - Hotel information
   - id, name, location, rating

2. **rooms** - Room inventory
   - id, hotel_id, room_number, room_type, price, status

3. **bookings** - Guest bookings
   - id, room_id, customer_name, customer_email, check_in_date, check_out_date, status, booking_date

4. **customers** - Guest information
   - id, name, email, phone, address, created_date

5. **users** - User accounts (INSECURE)
   - id, username, password (plaintext!)

### Sample Data
The database is auto-populated with:
- 3 sample hotels
- 6 sample rooms
- 1 sample booking
- 2 sample customers
- 1 sample user (admin/admin123)

---

## Known Issues & Vulnerabilities

### Critical Issues
1. **Overlapping Bookings** - No conflict detection when booking rooms
2. **Plain Text Passwords** - User passwords stored in plaintext
3. **No CSRF Protection** - Forms vulnerable to cross-site attacks
4. **No Input Validation** - Garbage data accepted
5. **Hardcoded Credentials** - Sample user hardcoded in database
6. **Debug Mode Enabled** - Exposes stack traces and internals
7. **Global Database Connections** - Not thread-safe

### Performance Issues
1. **No Pagination** - All records loaded for every query
2. **Duplicate Queries** - Same data fetched multiple times
3. **No Indexing** - Database has no indexes
4. **Inefficient Joins** - Multiple queries instead of single join
5. **No Caching** - All data fetched fresh every request

### Maintainability Issues
1. **1,000+ Lines in Single File** - Impossible to navigate
2. **Duplicate Code** - Logic repeated across routes
3. **No Tests** - Changes break things silently
4. **No Dependencies** - Only Flask, no utility libraries
5. **Magic Numbers** - Hardcoded values everywhere
6. **Poor Naming** - Generic variable names (user, data, result)

---

## Modernization Path

This application is designed to be incrementally modernized. Future improvements will include:

### Phase 1: Code Organization
- [ ] Modularize into separate files (models, routes, services)
- [ ] Create blueprints for different features
- [ ] Implement basic repository pattern

### Phase 2: Security & Validation
- [ ] Add input validation with Marshmallow or Pydantic
- [ ] Hash passwords with bcrypt
- [ ] Add CSRF protection with Flask-WTF
- [ ] Implement proper authentication/authorization

### Phase 3: Database & Persistence
- [ ] Migrate to SQLAlchemy ORM
- [ ] Implement database migrations with Alembic
- [ ] Add proper indexes
- [ ] Move to Azure SQL Database

### Phase 4: API & Testing
- [ ] Create REST API endpoints
- [ ] Add unit tests (pytest)
- [ ] Add integration tests
- [ ] Add API documentation (OpenAPI/Swagger)

### Phase 5: Cloud & DevOps
- [ ] Containerize with Docker
- [ ] Deploy to Azure App Service / Container Apps
- [ ] Add CI/CD pipeline (GitHub Actions)
- [ ] Implement logging with Application Insights
- [ ] Add monitoring and alerting

### Phase 6: Architecture
- [ ] Extract into microservices
- [ ] Implement service-to-service communication
- [ ] Add API Gateway
- [ ] Implement event-driven architecture
- [ ] Add distributed caching (Redis)

### Phase 7: Advanced Features
- [ ] Azure AD authentication
- [ ] Multi-tenancy
- [ ] Real-time updates (WebSockets)
- [ ] Advanced search (Elasticsearch)
- [ ] Business intelligence (Power BI)

---

## Running the Application

### Local Development
```bash
python app.py
```
Visit: http://localhost:5000

### Debug Info
The application prints debug information to console:
```
[DB] Database initialized successfully
[DB] Seeding database with sample data...
[DB] Sample data inserted successfully
[AUTH] User admin logged in
[ROOM] Room 101 added to hotel 1
...
```

### Accessing the App
1. Navigate to http://localhost:5000
2. You'll be redirected to /login
3. Log in with: admin / admin123
4. Browse hotels, rooms, bookings, customers

---

## Testing the Features

### Try These Scenarios
1. **Add Room** - Go to Rooms → Add New Room
2. **Create Booking** - Go to Bookings → Create New Booking (try overlapping dates!)
3. **Search** - Use the search bar to find hotels/rooms
4. **Edit Room** - Change room price or status
5. **Delete Room** - Delete a room (no integrity checks!)
6. **Add Customer** - Add duplicate email (no validation!)

---

## Environment Variables (Not Implemented)

The following should be environment variables but are hardcoded:
- `DATABASE_PATH` - Currently `"hotel.db"`
- `FLASK_ENV` - Currently always `"development"`
- `FLASK_DEBUG` - Currently always `True`
- `SECRET_KEY` - Currently `"hardcoded_insecure_key_12345"`
- `DATABASE_HOST` - Not applicable (local SQLite)
- `DATABASE_USER` - Not applicable
- `DATABASE_PASSWORD` - Not applicable
- `LOG_LEVEL` - Not implemented

---

## Dependencies

### Current (Minimal)
- Flask (web framework only)
- SQLite3 (included in Python)

### What Should Be Added
- Flask-SQLAlchemy (ORM)
- Flask-Migrate (database migrations)
- Flask-Login (authentication)
- Flask-WTF (forms + CSRF)
- Pydantic (validation)
- python-dotenv (environment config)
- pytest (testing)
- pytest-cov (coverage)
- black (code formatting)
- flake8 (linting)
- mypy (type checking)
- gunicorn (WSGI server)

---

## Deployment

### Current State
- **Development Only** - Requires `pip install flask` and `python app.py`
- **Local Database** - SQLite file on disk
- **No Scalability** - Single-threaded, no load balancing
- **No Monitoring** - No logging to external service
- **No Backups** - Database file not backed up

### Future Deployment (Post-Modernization)
```dockerfile
# Will use Docker for containerization
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "wsgi:app"]
```

---

## Troubleshooting

### Database File Exists
If `hotel.db` exists, delete it to reset:
```bash
rm hotel.db
python app.py
```

### Port Already in Use
Change the port in `app.py`:
```python
app.run(debug=True, host='0.0.0.0', port=5001)
```

### Import Error
Ensure Flask is installed:
```bash
pip install flask
```

### Can't Login
Use the demo credentials:
- **Username:** admin
- **Password:** admin123

---

## File Descriptions

### `app.py` (1000+ lines)
The ENTIRE application in one file. Contains:
- Database initialization
- All route handlers
- Business logic mixed with HTTP handling
- Raw SQL queries
- User authentication
- Search functionality
- Form processing

**This is the anti-pattern centerpiece.**

### `templates/base.html`
Base layout template with navigation. All pages extend this.
- No CSS framework
- Simple navigation bar
- Session-based login status
- Basic footer

### Feature Templates
- `index.html` - Hotel dashboard
- `hotel_detail.html` - Hotel details with rooms
- `rooms.html` - Room management list
- `add_room.html` - Form to add room
- `edit_room.html` - Form to edit room
- `bookings.html` - Booking list
- `add_booking.html` - Booking form (allows conflicts!)
- `customers.html` - Customer list
- `add_customer.html` - Add customer form
- `search_results.html` - Search results for all entity types
- `login.html` - Login page

### `static/style.css`
Basic CSS styling:
- No responsive design
- No media queries
- Minimal color scheme
- Table styling
- Form styling
- Button styling

---

## Performance Characteristics

### Database Queries
- Unindexed tables
- N+1 query problems (fetch list, then fetch detail for each)
- No query optimization
- All data loaded (no LIMIT)
- No prepared statements

### Memory Usage
- Entire result sets loaded into memory
- No pagination or streaming
- Global database connections

### Response Time
- Fast for small datasets (< 1000 records)
- Degrades as data grows
- No caching

---

## Future Architecture

The eventual modern architecture might look like:

```
┌─────────────────────────────────────────────────────┐
│              Azure Front Door / CDN                   │
├─────────────────────────────────────────────────────┤
│              React/Vue.js Frontend (SPA)              │
├─────────────────────────────────────────────────────┤
│          API Gateway / Azure API Management          │
├──────┬──────────┬──────────┬──────────┬──────────┐
│      │          │          │          │          │
▼      ▼          ▼          ▼          ▼          ▼
Hotels Rooms   Bookings Customers  Auth    Admin
Service Service Service  Service  Service  Service
│  │  │  │  │  │  │  │  │  │  │  │  │  │  │  │
└┬─┘  └┬─┘  └┬─┘  └┬─┘  └┬─┘  └┬──┘
 │     │     │     │     │     │
 └─────┴─────┴─────┴─────┴─────┤
                               │
               ┌───────────────┴─────────────┐
               │                             │
         ┌─────▼──────┐            ┌────────▼────────┐
         │  Azure SQL │            │ Azure Cache for │
         │  Database  │            │     Redis       │
         └────────────┘            └─────────────────┘

Plus:
- Azure Key Vault (secrets)
- Azure Monitor (logging)
- Application Insights (APM)
- Azure SignalR (real-time)
- Azure Service Bus (events)
- Azure Cosmos DB (eventual migration)
```

---

## Training Objectives

This application demonstrates the need for:

1. **Code Organization** - Single file becomes unmaintainable
2. **Separation of Concerns** - Mix of UI, logic, and data
3. **Database Abstraction** - Raw SQL is error-prone
4. **Input Validation** - Garbage data causes bugs
5. **Security** - Plain text passwords are dangerous
6. **Testing** - No tests = bugs everywhere
7. **Documentation** - Code is hard to understand
8. **Error Handling** - `print()` isn't a logging system
9. **Scalability** - Can't handle growth
10. **DevOps** - Manual deployment is painful

---

## References

### Modern Best Practices
- [Flask Best Practices](https://flask.palletsprojects.com/en/2.3.x/)
- [PEP 20 - The Zen of Python](https://www.python.org/dev/peps/pep-0020/)
- [SOLID Principles](https://en.wikipedia.org/wiki/SOLID)
- [12-Factor App](https://12factor.net/)
- [Clean Architecture](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)

### Azure Resources (Post-Modernization)
- [Azure App Service](https://docs.microsoft.com/en-us/azure/app-service/)
- [Azure Container Apps](https://docs.microsoft.com/en-us/azure/container-apps/)
- [Azure SQL Database](https://docs.microsoft.com/en-us/azure/azure-sql/database/)
- [Azure DevOps](https://docs.microsoft.com/en-us/azure/devops/)
- [Azure Monitor](https://docs.microsoft.com/en-us/azure/azure-monitor/)

---

## License

This is training material. No warranty is provided.

---

## Version History

- **v1.0** (2026-04-01) - Initial legacy monolith release
  - All features in single file
  - SQLite database
  - Hardcoded configuration
  - No security measures
  - No tests
  - Perfect starting point for modernization!

---

*Remember: This is intentionally bad. Learn what NOT to do!* 🚨
