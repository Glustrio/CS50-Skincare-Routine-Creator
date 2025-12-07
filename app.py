import os
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import login_required, usd, product_has_bad_ingredient, get_good_matches, product_has_fragrance, good_ingredients_by_skin_type, bad_ingredients_by_skin_type

# Configure application
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///skincare.db")

# So page doesn't cache things weird when logging in/out
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
    """Show user's dashboard with their saved routine"""

    # Get user ID from session
    user_id = session["user_id"]
    
    # Get user's skin type and username
    user = db.execute("SELECT username, skintype FROM users WHERE user_id = ?", user_id)
    
    # Get user's saved routine products (""" for multi-line string thingy)
    routine_products = db.execute("""
        SELECT products.id AS product_id, products.product_name, products.product_type, products.price_usd, products.product_url
        FROM products
        JOIN routine ON products.id = routine.product_id
        WHERE routine.user_id = ?
    """, user_id)
    
    # Get user's top 5 favorite products
    favorite_products = db.execute("""
        SELECT products.id AS product_id, products.product_name, products.product_type, products.price_usd
        FROM products
        JOIN favorites ON products.id = favorites.product_id
        WHERE favorites.user_id = ?
        LIMIT 5
    """, user_id)
    
    # Render the dashboard template with user info, routine, and favorites
    return render_template("index.html", 
                         user=user[0] if user else None,
                         routine=routine_products,
                         favorites=favorite_products)

@app.route("/search", methods=["GET", "POST"])
@login_required
def search():
    """Search for specific products"""

    # Handle search form submission
    if request.method == "POST":
        # Get form inputs
        query = request.form.get("query", "").strip() # Remove whitespace
        product_type = request.form.get("product_type", "")
        max_price = request.form.get("max_price", "")
        
        if not query and not product_type:
            flash("Please enter a search term or select a product type", "error")
            return render_template("search.html")
        
        # Build SQL query
        # Super neat trick by saying WHERE 1=1 (since it's always true)
        # Lets us append as many additional parameters as we'd like (mantains correct order too)
        sql = "SELECT * FROM products WHERE 1=1"
        params = []
        
        if query:
            sql += " AND product_name LIKE ?"
            params.append(f"%{query}%")
        
        if product_type:
            sql += " AND product_type = ?"
            params.append(product_type)
        
        if max_price:
            sql += " AND price_usd <= ?"
            params.append(float(max_price))
        
        sql += " LIMIT 50"
        
        results = db.execute(sql, *params)
        
        return render_template("search.html", results=results, query=query)
    # GET - show search form
    product_types = db.execute("SELECT DISTINCT product_type FROM products ORDER BY product_type")
    return render_template("search.html", product_types=product_types)

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
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

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

@app.route("/favorites", methods=["GET", "POST"])
@login_required
def favorites():
    """Show and manage favorite products"""
    user_id = session["user_id"]

    if request.method == "POST":
        product_id = request.form.get("product_id")
        action = request.form.get("action")

        if not product_id:
            flash("Product ID is required", "error")
            return redirect("/favorites")
        
        # Add product to favorites
        if action == "add":
            # Check if already favorited
            favorite_row = db.execute(
                "SELECT * FROM favorites WHERE user_id = ? AND product_id = ?",
                user_id, product_id)
            
            if not favorite_row:
                db.execute("INSERT INTO favorites (user_id, product_id) VALUES (?, ?)",
                          user_id, product_id)
                flash("Added to favorites!")
            else:
                flash("Already in favorites", "error")
        
        elif action == "remove":
            db.execute("DELETE FROM favorites WHERE user_id = ? AND product_id = ?",
                      user_id, product_id)
            flash("Removed from favorites")
        
        # Redirect to avoid resubmitting the form on refresh (or something like that)
        return redirect("/favorites")
    
    # If reached via GET, display favorite products
    favorites_row = db.execute("""
        SELECT products.id, products.product_name, products.product_type, products.price_usd, products.product_url
        FROM products
        JOIN favorites ON products.id = favorites.product_id
        WHERE favorites.user_id = ?
        ORDER BY products.product_type, products.product_name
    """, user_id)
    
    return render_template("favorites.html", favorites=favorites_row)

def filter_products(products, skin_type, concerns, fragrance_free):
    """Filter products based on user preferences"""
    filtered = []
    
    for product in products:
        # Skip if has bad ingredients for skin type
        if product_has_bad_ingredient(product, skin_type):
            continue
        
        # Skip if fragrance-free requested and product has fragrance
        if fragrance_free and product_has_fragrance(product):
            continue
        
        # Calculate match score based on good ingredients
        good_matches = get_good_matches(product["clean_ingreds"], skin_type)
        product["match_score"] = len(good_matches)
        product["good_ingredients"] = good_matches
        
        # Boost score if product addresses user concerns
        if "acne" in concerns and "salicylic acid" in product["clean_ingreds"]:
            product["match_score"] += 3
        if "hyperpigmentation" in concerns and any(ing in product["clean_ingreds"] 
            for ing in ["niacinamide", "vitamin c", "alpha arbutin"]):
            product["match_score"] += 3
        if "anti-aging" in concerns and any(ing in product["clean_ingreds"]
            for ing in ["retinol", "retinal", "peptides"]):
            product["match_score"] += 3
        if "dehydration" in concerns and "hyaluronic acid" in product["clean_ingreds"]:
            product["match_score"] += 3
        
        filtered.append(product)
    
    return filtered


def build_routine(products):
    """Build a complete AM/PM routine from filtered products"""
    
    # Define product types needed for each routine
    am_steps = ["Cleanser", "Toner", "Serum", "Moisturiser", "SPF"]
    pm_steps = ["Cleanser", "Exfoliator", "Serum", "Treatment", "Moisturiser"]
    
    routine = {
        "morning": [],
        "evening": []
    }
    
    # Group products by type
    by_type = {}
    for p in products:
        ptype = p["product_type"]
        if ptype not in by_type:
            by_type[ptype] = []
        by_type[ptype].append(p)
    
    # Sort each type by match score
    for ptype in by_type:
        by_type[ptype].sort(key=lambda x: x["match_score"], reverse=True)
    
    # Build morning routine
    for step in am_steps:
        if step in by_type and by_type[step]:
            routine["morning"].append(by_type[step][0])  # Best match
    
    # Build evening routine
    for step in pm_steps:
        if step in by_type and by_type[step]:
            # Use second-best cleanser if available (different from AM)
            if step == "Cleanser" and len(by_type[step]) > 1:
                routine["evening"].append(by_type[step][1])
            else:
                routine["evening"].append(by_type[step][0])
    
    return routine

@app.route("/routine", methods=["GET", "POST"])
@login_required
def routine():
    """Generate personalized skincare routine"""
    if request.method == "POST":
        skin_type = request.form.get("skin_type")
        concerns = request.form.getlist("concerns")  # Multiple checkboxes
        fragrance_free = request.form.get("fragrance_free")
        
        # Validation
        if not skin_type:
            flash("Please select your skin type", "error")
            return redirect("/preset")
        
        if not concerns:
            flash("Please select at least one concern", "error")
            return redirect("/preset")
        
        # Update user's skin type in database
        db.execute("UPDATE users SET skintype = ? WHERE user_id = ?", 
                  skin_type.capitalize(), session["user_id"])
        
        # Get all products with their ingredients
        products = db.execute("""
            SELECT p.id, p.product_name, p.product_type, p.price_usd, p.product_url,
                   GROUP_CONCAT(i.name) as ingredients
            FROM products p
            LEFT JOIN product_ingredients pi ON p.id = pi.product_id
            LEFT JOIN ingredients i ON pi.ingredient_id = i.ingredient_id
            GROUP BY p.id
        """)
        
        # Convert ingredients string back to list for each product
        for product in products:
            if product["ingredients"]:
                product["clean_ingreds"] = [ing.strip().lower() for ing in product["ingredients"].split(",")]
            else:
                product["clean_ingreds"] = []
        
        # Filter products based on criteria
        recommended = filter_products(products, skin_type.capitalize(), 
                                     concerns, fragrance_free)
        
        # Build routine structure
        routine = build_routine(recommended)
        
        return render_template("routine_results.html", 
                             routine=routine, 
                             skin_type=skin_type,
                             concerns=concerns)
    
    # GET request - show the form
    return redirect("/preset")

@app.route("/save_routine", methods=["POST"])
@login_required
def save_routine():
    """Save the recommended routine to the user's account"""
    user_id = session["user_id"]
    product_ids = request.form.getlist("product_ids")
    
    if not product_ids:
        flash("There's no products to save bruh", "error")
        return redirect("/preset")
    
    # Clear existing routine
    db.execute("DELETE FROM routine WHERE user_id = ?", user_id)
    
    # Save new routine
    for product_id in product_ids:
        db.execute("INSERT INTO routine (user_id, product_id) VALUES (?, ?)",
                  user_id, product_id)
    
    flash("Routine saved successfully!")
    return redirect("/")

@app.route("/product/<int:product_id>") # Makes product_id an int
@login_required
def product_detail(product_id):
    """Show detailed product information"""
    # Get product info
    product = db.execute("SELECT * FROM products WHERE id = ?", product_id)
    
    if not product:
        flash("Product not found", "error")
        return redirect("/search")
    
    # Get ingredients
    ingredients = db.execute("""
        SELECT i.name
        FROM ingredients i
        JOIN product_ingredients pi ON i.ingredient_id = pi.ingredient_id
        WHERE pi.product_id = ?
        ORDER BY i.name
    """, product_id)
    
    # Check if favorited
    is_favorite = db.execute(
        "SELECT * FROM favorites WHERE user_id = ? AND product_id = ?",
        session["user_id"], product_id
    )
    
    # Get user's skin type for ingredient analysis
    user = db.execute("SELECT skintype FROM users WHERE user_id = ?", session["user_id"])
    skin_type = user[0]["skintype"] if user else "Combination"
    
    # Analyze ingredients
    ingredient_names = [ing["name"] for ing in ingredients]
    
    good_ings = [ing for ing in ingredient_names 
                if ing in good_ingredients_by_skin_type.get(skin_type, [])]
    bad_ings = [ing for ing in ingredient_names 
               if ing in bad_ingredients_by_skin_type.get(skin_type, [])]
    
    return render_template("product_detail.html", 
                         product=product[0],
                         ingredients=ingredient_names,
                         good_ingredients=good_ings,
                         bad_ingredients=bad_ings,
                         is_favorite=bool(is_favorite))