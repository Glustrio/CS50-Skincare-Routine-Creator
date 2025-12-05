import os
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, usd, product_has_bad_ingredient, get_good_matches, product_has_fragrance

# Configure application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///skincare.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    return render_template("index.html")


@app.route("/search", methods=["GET", "POST"])
@login_required
def search():
    """search for items"""
    return render_template("apology.html")


@app.route("/favorites")
@login_required
def favorites():
    """Show favorite products"""
    return render_template("apology.html")

@app.route("/preset")
@login_required
def preset():
    """Show Preset Skincare Routine Builder"""
    return render_template("preset.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            flash("must provide username", category="error")
            return render_template("login.html")

        # Ensure password was submitted
        elif not request.form.get("password"):
            flash("must provide password", category="error")
            return render_template("login.html")

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            flash("invalid username and/or password", category="error")
            return render_template("login.html")

        # Remember which user has logged in
        session["user_id"] = rows[0]["user_id"] #second user_id was changed from id

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # Forget any user_id and clears session before registering a new user to ensure no previous session data interferes with registration
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            flash("must provide username", category="error")
            return render_template("register.html")

        # Ensure password was submitted
        elif not request.form.get("password"):
            flash("must provide password", category="error")
            return render_template("register.html")

        elif not request.form.get("confirmation"):
            flash("must provide password confirmation", category="error")
            return render_template("register.html")

        elif request.form.get("confirmation") != request.form.get("password"):
            flash("password must match", category="error")
            return render_template("register.html")     

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username does not exist
        if len(rows) != 0:
           flash("username already taken", category="error")
           return render_template("register.html")

        # Insert the new user into users in our database, storing a hash of the user's password, not the password itself
        db.execute("INSERT INTO users (username, hash, skintype) VALUES(?, ?, ?)", request.form.get(
            "username"), generate_password_hash(request.form.get("password")), request.form.get("skintype"))

        # Look up the new user's user_id
        row = db.execute(
            "SELECT user_id FROM users WHERE username = ?",
            request.form.get("username")
        )

        # Log user in by setting session["user_id"]
        session["user_id"] = row[0]["user_id"]

        flash("Registered!")

        # Redirect user to home page
        return redirect("/")

    # When requested via GET, display registration form
    else:
        return render_template("register.html")


