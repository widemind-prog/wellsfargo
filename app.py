from flask import (
    Flask, render_template, request, redirect,
    session, url_for, flash, send_from_directory
)
from functools import wraps
import os

# -------------------------------
# APP SETUP
# -------------------------------
app = Flask(__name__)
app.secret_key = "dummy-secret"

BASE_DIR = os.getcwd()
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads", "screenshots")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# -------------------------------
# DUMMY USERS
# -------------------------------
DUMMY_USER = {
    "username": "demo",
    "password": "demo123",
    "name": "Wide Mind User"
}

ADMIN_USER = {
    "username": "admin",
    "password": "admin123",
    "name": "Admin"
}

# -------------------------------
# DUMMY DATA
# -------------------------------
DUMMY_ACCOUNTS = [
    {"id": 1, "type": "Checking", "balance": 15240.75, "number": "**** **** **** 4821"},
    {"id": 2, "type": "Savings", "balance": 8240.50, "number": "**** **** **** 3950"},
    {"id": 3, "type": "Deposits", "balance": 5020.00, "number": "**** **** **** 1298"},
]

DUMMY_TRANSACTIONS = {
    1: [
        {"desc": "POS Purchase - AMAZON", "amount": -250.00},
        {"desc": "Payment Received", "amount": 1500.00},
    ],
    2: [
        {"desc": "Interest Credited", "amount": 12.50},
        {"desc": "Deposit via Mobile", "amount": 500.00},
    ],
    3: [
        {"desc": "Deposit Matured", "amount": 2000.00},
        {"desc": "Withdrawal", "amount": -500.00},
    ],
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
    return render_template("login.html")


@app.route("/login", methods=["POST"])
def do_login():
    username = request.form["username"]
    password = request.form["password"]

    if username == ADMIN_USER["username"] and password == ADMIN_USER["password"]:
        session["user"] = ADMIN_USER["name"]
        session["role"] = "admin"
        return redirect("/uploads")

    if username == DUMMY_USER["username"] and password == DUMMY_USER["password"]:
        session["user"] = DUMMY_USER["name"]
        session["role"] = "user"
        return redirect("/accounts")

    return redirect("/")

# -------------------------------
# USER ROUTES
# -------------------------------
@app.route("/accounts")
@login_required
def accounts():
    return render_template("accounts.html", accounts=DUMMY_ACCOUNTS)


@app.route("/accounts/<int:account_id>")
@login_required
def account_details(account_id):
    account = next((a for a in DUMMY_ACCOUNTS if a["id"] == account_id), None)
    if not account:
        return "Account not found", 404

    transactions = DUMMY_TRANSACTIONS.get(account_id, [])
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
# OTHER PAGES
# -------------------------------
@app.route("/cards")
@login_required
def cards():
    # Generate cards from accounts
    cards = []

    for acc in DUMMY_ACCOUNTS:
        cards.append({
            "brand": "Visa" if acc["id"] % 2 else "MasterCard",
            "number": acc["number"],
            "note": f"{acc['type']} Account Card"
        })

    return render_template(
        "cards.html",
        cards=cards
    )


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