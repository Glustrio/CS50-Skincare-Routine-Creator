# GlowGuide Design Document

GlowGuide is a Flask-based full-stack web application designed to generate personalized skincare routines based on product ingredients, user skin types, concerns, and budget preferences. The system integrates a Kaggle skincare dataset, ingredient-matching logic, user account management, favoriting features, routine saving, and detailed product analysis.
This design document explains the overall architecture, route logic, database structure, algorithmic decisions, template inheritance, and tradeoffs made during development.

## High-level Architecture
Underneath the hood, GlowGuide relies on our SQLite 'skincare.db' database which contains tables for users, products, product_ingredients, favorites, and routine. 

`app.py` and `helpers.py` work to handle the application logic, taking are of routing, form validation, database queries, scoring algorithms, and session management. 

The remaining HTML files in the `templates` folder are all Jinja templates inhereting from layout.html. They are also all responsive UI built with Bootstrap and some CSS styling. The templates include: the dashboard (`index.html`), routine generator (`preset.html`, `routine_results.html`), search page (`search.html`), favorites (`favorites.html`), product detail (`product_detail.html`), and authentication pages (`login.html`, `register.html`).

## Directory Structure
```
.
├── app.py
├── helpers.py
├── skincare_setup.py
├── skincare.db
├── /templates
│   ├── layout.html
│   ├── index.html
│   ├── preset.html
│   ├── routine_results.html
│   ├── search.html
│   ├── favorites.html
│   ├── login.html
│   ├── register.html
│   ├── resources.html
│   ├── product_detail.html
├── /static
│   └── styles.css
├──requirements.txt
├── DESIGN.md
└── README.md
```

## Authentication System
GlowGuide includes a full registration and login system.Passwords are hashed using Werkzeug’s security utilities, with username and hashed passwords stored in the users table. A user session stores user_id for authenticated access.'login_required' decorator prevents unauthorized access to the main website. Session management is handled by Flask-Session, storing session data on the filesystem for security and persistence.

## Dataset Pre-processing & Ingredient Logic
The products table in `skincare.db` was curated by preprocessing the Skincare Products Clean Dataset on Kaggle linked here (https://www.kaggle.com/datasets/eward96/skincare-products-clean-dataset). The file is cleaned, normalized, and imported into `skincare.db` using skincare_setup.py.
Each product stores a name, price, product type, ingredient list (as comma-separated or cleaned text), and product URL. Ingredients are categorized internally as beneficial, potentially irritating or comedogenic, or neutral for certain skin types or concerns.
For a logged-in user, product evaluation is customized based on their skin type and/or selected concerns. For example, for oily skin, salicylic acid and niacinamide is helpful, but heavy oils are not. For dry skin, ceramides and glycerin are helpful, but harsh exfoliants are not. 
The algorithm checks for keywords inside each product’s ingredient list, generating `good_ingredients`, `bad_ingredients`, `match_score` the three of which help to power routine generation, product search highlights, and product detail ingredient analysis.

## Routine Generation Algorithm
Generating a routine takes the following steps:
1. User input (from `preset.html`) which includes skin type, at least one concern, optional budget limit, and optional fragrance-free filter.
2. A database query that filters products by price threshold, product category, ingredient requirements, fragrance-free preference, and relevant concerns.
3. A number score for each product based on the number of helpful ingredients, the number of harmful ingredients,  alignment with user concerns, and fit for morning or evening categories.
4. Categorization of each product into either Morning Routine (e.g. vitamin C, hydrating serums, moisturizers) or Evening Routine (e.g. retinoids, exfoliants, occlusives).
5. Finally the products are rendered into `routine_results.html` with the ordered steps of the routine, match score, ingredient summary, pricing, total routine cost, and the save routine option.
When a routine is saved, product ids are inserted into `routine_items` for the current user. The dashboard (`index.html`) retrieves and displays the routine. Users may overwrite their routine by saving a new one. People new to skincare often don't even know where to start, and usually have a strict budget. Parsing through the ingredients list of a product can be confusing and tedious. By generating a routine for the user based on their concerns and skin type, we make it so users don't have to spend as much time researching on their own. 

## Search System
The search tool (implemented in /search route) allows users to query by name, filter by type, and filter by maximum price.
The background logic consists of constructing a SQL query dynamically based on user-provided fields, executing the query and return matching products, and displaying results with product name, price, type, and an "Add to Favorites" button. Including a search system seemed natural since most of the time people are just looking for one or two products to round out their routine. Allowing to filter based on price and type helps to narrow down the search as well.

## Favorites System
Favorites are stored in a favorites table mapping user_id and product_id. The system supports adding favorites, removing favorites, preventing duplicate entries, displaying total value of favorites, and rendering the favorited products in one place (`favorites.html`). Often, people may want a product but can't afford it at the time, so having a feature to save it for later is helpful in case users forget. Separating routines and favorites provides flexibility so users can experiment without overwriting their saved routine.

## Product Detail Page
In a product detail page, you'll find the product name, type, and price. You'll also find the ability to add or remove the product from favorites, a link to the external product page, and ingredient analysis that highlights the good and bad ingredients in a product, and a skin compatibility alert. The /product/<id> route retrieves product data, ingredient list, good ingredients, bad ingredients, and favorite status. It then renders the product detail template and provides evaluation based on the user's skin type. Sometimes you want to know if a specific product is good for your skin, so being able to see the analysis of exactly what ingredients are good or bad can be very insightful.

