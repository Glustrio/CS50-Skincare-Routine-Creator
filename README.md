# GlowGuide -- Personalized Skincare Routine Creator
*CS50 Final Project by Gordon & Jacob*

GlowGuide is a Flask web application that helps users create personaized skincare routines based on product ingredient data, user preferences, and skincare concerns. The goal of the project is to make skincare simple, approachable, and data-backed--especially users who are just beginning to build a routine. Upon accessing the GlowGuide, users will be able to register an account and log in, generate morning and evening skincare routines using our preset builder, search for skincare products from a Kaggle dataset (https://www.kaggle.com/datasets/eward96/skincare-products-clean-dataset), view detailed information about each product, save a custom routine to their profile, and favorite products for quick access later.

## Installation Guide:

The project folder should include the following files and structure:
'''
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
'''

Install the required dependencies by running in the terminal:
'pip install -r requirements.txt'

To run the application, from the terminal:
1. Navigate to your project folder
2. Set Flask environment variable with 'export FLASK_APP=app.py'
3. Start the web server with 'flask run'
4. Open the provided URL 
5. Enjoy :D

## Usage Guide: 

When you first open up the web application, the you're redirected to the login page of the application. If you already have an account somehow or can "guess" someone else's username password, you can log in with the correct username and password stored in the database. If you don't have an account, you can click on the register button on the right. You'll be prompted to enter an username and password, confirm the password, choose a skin type. After all those are fulfilled, then you can click register to create an account with all those information stored in your user in our database. 

Now that you have an account with an username and password, you could log in if registering didn't automatically log you in already. You can click log out too if you want to log out and clear the session. After logging in, you'll see the index page with the welcome section displaying your username and skin type. The index page also displays your saved routine if you want one, recent favorites, and skincare tips. 

Navigate to Preset Routines to create a custom AM/PM routine where you will select a skin type, your main concerns (acne, hyperpigmentation, dehydration, sensitivity, anti-aging), budget filter (optional), and fragrance-free requirement (optional). When you submit the form, the website analyzes product ingredients and matches products to your concerns. It then separates them into Morning Routine and Evening Routine and calculates the total cost of your routine. From the results page, you may view detailed product pages (displaying specific ingredients, the option to favorite individual products, and a link to purchase the product), save the generated routine to your account, or generate a new one. If you save a routine, it appears on your Dashboard and includes product names, types, prices, and links to purchase pages. Users may replace their routine at any time by generating a new one.

Go to the Search page to browse the full product database.
You can search by product name (optional), filter by product type (cleanser, moisturizer, serum, etc.), and/or filter by maximum price. The search results will display product names, product types, price, and a button to favorite the product. Selecting a product shows its full details, ingredient list, recommended use, and purchase link where available.

The Favorites page allows you to view all items you've favorited, visit product detail pages, remove items from your favorites, see the total number of favorites, and view the combined price of all favorited products. Favorites are stored in the database so they persist between sessions.

Youtube Video: [CS50 Final Project: GlowGuide](https://www.youtube.com/watch?v=MsWHJcL2K7g)