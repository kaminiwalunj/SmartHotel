"""SmartHotel Management System"""

import logging
import os
import re
import sqlite3
from functools import wraps

from dotenv import load_dotenv
from flask import Flask, g, jsonify, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

load_dotenv()

# ===== LOGGING =====
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("smarthotel")

# ===== APPLICATION SETUP =====
app = Flask(__name__)

app.secret_key = os.getenv("SECRET_KEY")
if not app.secret_key:
    raise ValueError(
        "SECRET_KEY environment variable is not set.\n"
        "  Local dev: create a .env file (see .env.example)\n"
        "  Azure: set it in App Service Configuration or Key Vault"
    )

app.debug = os.getenv("FLASK_DEBUG", "false").lower() == "true"

DATABASE = os.getenv("DATABASE_PATH", "hotel.db")


# ===== DATABASE HELPERS =====

def get_db():
    """Return a per-request database connection stored on Flask's `g` object."""
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


@app.teardown_appcontext
def close_db(exception):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv


def modify_db(query, args=()):
    db = get_db()
    db.execute(query, args)
    db.commit()


# ===== AUTH DECORATOR =====

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated


EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


# ===== DATABASE INITIALIZATION =====

def init_db():
    """Initialize database schema and seed sample data if needed.
    
    Safe to call multiple times - uses CREATE TABLE IF NOT EXISTS
    to avoid errors on subsequent calls.
    """
    db = sqlite3.connect(DATABASE)
    db.execute("PRAGMA foreign_keys = ON")
    cur = db.cursor()

    cur.execute('''
        CREATE TABLE IF NOT EXISTS hotels (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            location TEXT NOT NULL,
            rating REAL DEFAULT 0
        )
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS rooms (
            id INTEGER PRIMARY KEY,
            hotel_id INTEGER NOT NULL,
            room_number TEXT NOT NULL,
            room_type TEXT NOT NULL,
            price REAL NOT NULL,
            status TEXT DEFAULT 'available',
            FOREIGN KEY (hotel_id) REFERENCES hotels(id)
        )
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY,
            room_id INTEGER NOT NULL,
            customer_name TEXT NOT NULL,
            customer_email TEXT,
            check_in_date TEXT NOT NULL,
            check_out_date TEXT NOT NULL,
            status TEXT DEFAULT 'active',
            booking_date TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (room_id) REFERENCES rooms(id)
        )
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT,
            address TEXT,
            created_date TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL
        )
    ''')

    db.commit()
    logger.info("Database schema initialized")

    if cur.execute("SELECT COUNT(*) FROM hotels").fetchone()[0] == 0:
        logger.info("Seeding sample data")

        cur.execute("INSERT INTO hotels (name, location, rating) VALUES ('Grand Plaza Hotel', 'New York', 4.5)")
        cur.execute("INSERT INTO hotels (name, location, rating) VALUES ('Ocean View Resort', 'Miami', 4.2)")
        cur.execute("INSERT INTO hotels (name, location, rating) VALUES ('Mountain Peak Hotel', 'Denver', 3.8)")

        cur.execute("INSERT INTO rooms (hotel_id, room_number, room_type, price, status) VALUES (1, '101', 'Single', 99.99, 'available')")
        cur.execute("INSERT INTO rooms (hotel_id, room_number, room_type, price, status) VALUES (1, '102', 'Double', 149.99, 'available')")
        cur.execute("INSERT INTO rooms (hotel_id, room_number, room_type, price, status) VALUES (1, '103', 'Suite', 249.99, 'booked')")
        cur.execute("INSERT INTO rooms (hotel_id, room_number, room_type, price, status) VALUES (2, '201', 'Single', 89.99, 'available')")
        cur.execute("INSERT INTO rooms (hotel_id, room_number, room_type, price, status) VALUES (2, '202', 'Double', 139.99, 'available')")
        cur.execute("INSERT INTO rooms (hotel_id, room_number, room_type, price, status) VALUES (3, '301', 'Single', 79.99, 'available')")

        cur.execute("INSERT INTO bookings (room_id, customer_name, customer_email, check_in_date, check_out_date, status) VALUES (3, 'John Doe', 'john@example.com', '2026-04-05', '2026-04-10', 'active')")

        cur.execute("INSERT INTO customers (name, email, phone, address) VALUES ('John Doe', 'john@example.com', '555-1234', '123 Main St')")
        cur.execute("INSERT INTO customers (name, email, phone, address) VALUES ('Jane Smith', 'jane@example.com', '555-5678', '456 Oak Ave')")

        pw_hash = generate_password_hash(os.getenv("ADMIN_PASSWORD", "admin123"))
        cur.execute("INSERT INTO users (username, password_hash) VALUES ('admin', ?)", (pw_hash,))

        db.commit()
        logger.info("Sample data inserted")

    db.close()


# ===== LAZY DATABASE INITIALIZATION =====

_db_initialized = False

def ensure_db_initialized():
    """Initialize database on first request if not already done."""
    global _db_initialized
    if not _db_initialized:
        init_db()
        _db_initialized = True


@app.before_request
def before_request():
    """Ensure database is initialized before handling any request."""
    ensure_db_initialized()


# ===== HEALTH CHECK =====

@app.route("/health")
def health():
    """Lightweight health check - returns immediately without DB access."""
    return jsonify({"status": "healthy"}), 200


# ===== AUTH ROUTES =====

@app.route("/")
@login_required
def index():
    hotels = query_db("SELECT * FROM hotels")
    return render_template("index.html", hotels=hotels)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        user = query_db(
            "SELECT * FROM users WHERE username = ?", (username,), one=True
        )

        if user and check_password_hash(user["password_hash"], password):
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            logger.info("User logged in: %s", username)
            return redirect(url_for("index"))

        logger.warning("Failed login attempt for: %s", username)
        return render_template("login.html", error="Invalid credentials"), 401

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# ===== HOTEL ROUTES =====

@app.route("/hotels/view/<int:hotel_id>")
@login_required
def view_hotel(hotel_id):
    hotel = query_db("SELECT * FROM hotels WHERE id = ?", (hotel_id,), one=True)
    if not hotel:
        return "Hotel not found", 404
    rooms = query_db("SELECT * FROM rooms WHERE hotel_id = ?", (hotel_id,))
    return render_template("hotel_detail.html", hotel=hotel, rooms=rooms)


# ===== ROOM ROUTES =====

@app.route("/rooms")
@login_required
def rooms():
    all_rooms = query_db(
        "SELECT r.*, h.name AS hotel_name "
        "FROM rooms r JOIN hotels h ON r.hotel_id = h.id"
    )
    hotels = {row["id"]: row for row in query_db("SELECT * FROM hotels")}
    return render_template("rooms.html", rooms=all_rooms, hotels=hotels)


@app.route("/rooms/add", methods=["GET", "POST"])
@login_required
def add_room():
    if request.method == "POST":
        hotel_id = request.form.get("hotel_id")
        room_number = request.form.get("room_number", "").strip()
        room_type = request.form.get("room_type", "").strip()
        price = request.form.get("price")

        if not all([hotel_id, room_number, room_type, price]):
            return "Missing required fields", 400
        try:
            price_val = float(price)
        except (TypeError, ValueError):
            return "Invalid price", 400

        existing = query_db(
            "SELECT id FROM rooms WHERE hotel_id = ? AND room_number = ?",
            (hotel_id, room_number),
            one=True,
        )
        if existing:
            return "Room number already exists in this hotel", 409

        modify_db(
            "INSERT INTO rooms (hotel_id, room_number, room_type, price, status) VALUES (?, ?, ?, ?, ?)",
            (hotel_id, room_number, room_type, price_val, "available"),
        )
        logger.info("Room %s added to hotel %s", room_number, hotel_id)
        return redirect(url_for("rooms"))

    hotels = query_db("SELECT * FROM hotels")
    return render_template("add_room.html", hotels=hotels)


@app.route("/rooms/edit/<int:room_id>", methods=["GET", "POST"])
@login_required
def edit_room(room_id):
    if request.method == "POST":
        room_number = request.form.get("room_number", "").strip()
        room_type = request.form.get("room_type", "").strip()
        price = request.form.get("price")
        status = request.form.get("status", "").strip()

        if not room_number or not room_type:
            return "Invalid input", 400
        try:
            price_val = float(price)
        except (TypeError, ValueError):
            return "Invalid price", 400

        modify_db(
            "UPDATE rooms SET room_number = ?, room_type = ?, price = ?, status = ? WHERE id = ?",
            (room_number, room_type, price_val, status, room_id),
        )
        logger.info("Room %d updated", room_id)
        return redirect(url_for("rooms"))

    room = query_db("SELECT * FROM rooms WHERE id = ?", (room_id,), one=True)
    if not room:
        return "Room not found", 404
    return render_template("edit_room.html", room=room)


@app.route("/rooms/delete/<int:room_id>", methods=["POST"])
@login_required
def delete_room(room_id):
    active = query_db(
        "SELECT id FROM bookings WHERE room_id = ? AND status = 'active'",
        (room_id,),
        one=True,
    )
    if active:
        return "Cannot delete room with active bookings", 409

    modify_db("DELETE FROM rooms WHERE id = ?", (room_id,))
    logger.info("Room %d deleted", room_id)
    return redirect(url_for("rooms"))


# ===== BOOKING ROUTES =====

@app.route("/bookings")
@login_required
def bookings():
    all_bookings = query_db(
        "SELECT b.*, r.room_number, r.room_type, h.name AS hotel_name "
        "FROM bookings b "
        "JOIN rooms r ON b.room_id = r.id "
        "JOIN hotels h ON r.hotel_id = h.id "
        "ORDER BY b.booking_date DESC"
    )
    return render_template("bookings.html", bookings=all_bookings)


@app.route("/bookings/add", methods=["GET", "POST"])
@login_required
def add_booking():
    if request.method == "POST":
        room_id = request.form.get("room_id")
        customer_name = request.form.get("customer_name", "").strip()
        customer_email = request.form.get("customer_email", "").strip()
        check_in = request.form.get("check_in_date", "").strip()
        check_out = request.form.get("check_out_date", "").strip()

        if not all([room_id, customer_name, check_in, check_out]):
            return "Missing required fields", 400
        if check_out <= check_in:
            return "Check-out must be after check-in", 400

        overlap = query_db(
            "SELECT id FROM bookings "
            "WHERE room_id = ? AND status = 'active' "
            "AND check_in_date < ? AND check_out_date > ?",
            (room_id, check_out, check_in),
            one=True,
        )
        if overlap:
            return "Room is already booked for those dates", 409

        db = get_db()
        db.execute(
            "INSERT INTO bookings (room_id, customer_name, customer_email, "
            "check_in_date, check_out_date, status) VALUES (?, ?, ?, ?, ?, ?)",
            (room_id, customer_name, customer_email, check_in, check_out, "active"),
        )
        db.execute("UPDATE rooms SET status = ? WHERE id = ?", ("booked", room_id))
        db.commit()

        logger.info("Booking created for room %s", room_id)
        return redirect(url_for("bookings"))

    available_rooms = query_db(
        "SELECT r.*, h.name AS hotel_name "
        "FROM rooms r JOIN hotels h ON r.hotel_id = h.id "
        "WHERE r.status = ?",
        ("available",),
    )
    return render_template("add_booking.html", rooms=available_rooms)


@app.route("/bookings/cancel/<int:booking_id>", methods=["POST"])
@login_required
def cancel_booking(booking_id):
    booking = query_db(
        "SELECT room_id FROM bookings WHERE id = ?", (booking_id,), one=True
    )
    if not booking:
        return "Booking not found", 404

    db = get_db()
    db.execute("UPDATE bookings SET status = ? WHERE id = ?", ("cancelled", booking_id))
    db.execute("UPDATE rooms SET status = ? WHERE id = ?", ("available", booking["room_id"]))
    db.commit()

    logger.info("Booking %d cancelled", booking_id)
    return redirect(url_for("bookings"))


# ===== CUSTOMER ROUTES =====

@app.route("/customers")
@login_required
def customers():
    all_customers = query_db("SELECT * FROM customers ORDER BY created_date DESC")
    return render_template("customers.html", customers=all_customers)


@app.route("/customers/add", methods=["GET", "POST"])
@login_required
def add_customer():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        phone = request.form.get("phone", "").strip()
        address = request.form.get("address", "").strip()

        if not name or not email:
            return "Missing required fields", 400
        if not EMAIL_RE.match(email):
            return "Invalid email address", 400

        existing = query_db(
            "SELECT id FROM customers WHERE email = ?", (email,), one=True
        )
        if existing:
            return "A customer with this email already exists", 409

        modify_db(
            "INSERT INTO customers (name, email, phone, address) VALUES (?, ?, ?, ?)",
            (name, email, phone, address),
        )
        logger.info("Customer added: %s", name)
        return redirect(url_for("customers"))

    return render_template("add_customer.html")


# ===== SEARCH =====

@app.route("/search", methods=["GET"])
@login_required
def search():
    query = request.args.get("q", "").strip()
    if len(query) < 2:
        return "Search query too short", 400

    like = f"%{query}%"
    results = {
        "hotels": query_db(
            "SELECT * FROM hotels WHERE name LIKE ? OR location LIKE ?",
            (like, like),
        ),
        "rooms": query_db(
            "SELECT r.*, h.name AS hotel_name "
            "FROM rooms r JOIN hotels h ON r.hotel_id = h.id "
            "WHERE r.room_number LIKE ? OR r.room_type LIKE ?",
            (like, like),
        ),
        "customers": query_db(
            "SELECT * FROM customers WHERE name LIKE ? OR email LIKE ?",
            (like, like),
        ),
    }
    return render_template("search_results.html", query=query, results=results)


# ===== ERROR HANDLERS =====

@app.errorhandler(404)
def not_found(error):
    logger.warning("404: %s", request.path)
    return "Page not found", 404


@app.errorhandler(500)
def server_error(error):
    logger.exception("Internal server error")
    return "Internal server error", 500


if __name__ == "__main__":
    # Note: Database initialization now happens lazily via @app.before_request hook
    # (see ensure_db_initialized) on first request, so we don't call init_db() here.
    host = os.getenv("FLASK_HOST", "127.0.0.1")
    port = int(os.environ.get("PORT", os.getenv("FLASK_PORT", "5000")))
    app.run(debug=app.debug, host=host, port=port)
