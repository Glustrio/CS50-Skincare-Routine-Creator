import os
from flask import Flask, render_template, request, redirect, session, flash
from cs50 import SQL
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import login_required, apology

app = Flask(__name__)

app.secret_key = os.urandom(24)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///skincare.db")


@app.route("/")
@login_required
def index():
    return render_template("index.html")


@app.route("/routine", methods=["POST"])
@login_required
def routine():
    # Get user inputs
    skin_type = request.form.get("skin_type")
    concerns = request.form.getlist("concerns")  # list of concerns
    fragrance_free = request.form.get("fragrance_free")  # 'on' or None

    if not skin_type or not concerns:
        # Minimal validation
        return render_template("index.html", error="Please select a skin type and at least one concern.")

    # For now, just use the first concern as "primary"
    primary_concern = concerns[0]

    pref_ff = 1 if fragrance_free == "on" else None

    # Helper to build query with optional fragrance filter
    def get_product(step):
        query = """
            SELECT * FROM products
            WHERE step = ?
            AND skin_types LIKE ?
            AND concerns LIKE ?
        """
        params = [step, f"%{skin_type}%", f"%{primary_concern}%"]

        if pref_ff is not None:
            query += " AND fragrance_free = ?"
            params.append(pref_ff)

        # For now, just pick the cheapest that matches
        query += " ORDER BY price ASC LIMIT 1"

        rows = db.execute(query, *params)
        if rows:
            return rows[0]
        else:
            return None

    # Build morning and evening routines
    morning = {
        "cleanser": get_product("cleanser"),
        "serum": get_product("serum"),
        "moisturizer": get_product("moisturizer"),
        "sunscreen": get_product("sunscreen")
    }

    evening = {
        "cleanser": get_product("cleanser"),
        "serum": get_product("serum"),
        "moisturizer": get_product("moisturizer")
        # You can add "treatment" if you have those
    }

    return render_template(
        "results.html",
        skin_type=skin_type,
        primary_concern=primary_concern,
        morning=morning,
        evening=evening
    )

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

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
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        elif not request.form.get("confirmation"):
            return apology("must provide password confirmation", 400)

        elif request.form.get("confirmation") != request.form.get("password"):
            return apology("password must match", 400)

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username does not exist
        if len(rows) != 0:
            return apology("username already taken", 400)

        # Insert the new user into users in our database, storing a hash of the user's password, not the password itself
        db.execute("INSERT INTO users (username, hash) VALUES(?, ?)", request.form.get(
            "username"), generate_password_hash(request.form.get("password")))

        # Store the id of the newly created user into user_id to keep track of it with session
        user_id = db.execute(
            "SELECT id FROM users WHERE username = ?", request.form.get("username")
        )

        # Log user in by setting session["user_id"] to the new id of whatever user we just added to the database
        session["user_id"] = user_id[0]["id"]

        flash("Registered!")

        # Redirect user to home page
        return redirect("/")

    # When requested via GET, display registration form
    else:
        return render_template("register.html")

if __name__ == "__main__":
    app.run(debug=True)