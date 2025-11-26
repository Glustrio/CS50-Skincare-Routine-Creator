import os
from flask import Flask, render_template, request
from cs50 import SQL  # or use sqlite3 if you prefer

app = Flask(__name__)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///skincare.db")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/routine", methods=["POST"])
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


if __name__ == "__main__":
    app.run(debug=True)