# CS50-Skincare-Routine-Creator

Our CS50 Skincare Routine Creator is named Gordon & Jacob's GlowGuide or GlowGuide for short. The web application was inspired by CS50 functions and helps users create a personalized skincare routine. After registering for an account and signing in, users can select a skin type and skincare concerns with our preset skincare routine creator, generate a morning and night routine based on skincare product ingredients, search for products from a large database found from Kaggle, save a routine to their account, favorite products, and view product details. This project hopes to make skincare simpler for people/users who are starting to look into starting skincare.

Glowguide is designed to run on codespace using flask and sql. To run the web application, go to your codespace, open your terminal and go into your project folder. The folder should contain files like app.py, helpers.py, skincare_setup.py,
skincare.db, templates containing layout.html, index.html, login.html, register.html, search.html, favorites.html, preset.html, routine_results.html, product_detail.html, login.html, README.md (user guide), DESIGN.md (technical write-up), and requirements.txt.

Then run the web app by using flask run in the terminal and then accessing it in ports by using the forwarded address to open it and access the web application. 

Usage Guide: 

When you first open up the web application, the you're redirected to the login page of the application. If you already have an account somehow or can "guess" someone else's username password, you can log in with the correct username and password stored in the database. If you don't have an account, you can click on the register button on the right. You'll be prompted to enter an username and password, confirm the password, choose a skin type. After all those are fulfilled, then you can click register to create an account with all those information stored in your user in our database. 

Now that you have an account with an username and password, you could log in if registering didn't automatically log you in already. You can click log out too if you want to log out and clear the session.

After logging in, you'll see the index page with the welcome section displaying your username and skin type. The index page also displays your saved routine if you want one, recent favorites, and skincare tips. From here, you can navigate to the nav bar (or create your first routine) and go to preset routines to generate a skincare routine based off the chosen skin type and skin conditions. You could also start searching for products from a database we found from Kaggle by clicking on the start searching button of the index page or navigating to the search page through the navigation bar search button. You can also navigate to favorites to view all your favorite products. In the search bar, you can search for a product by name and filter by choosing the type of product it is (e.g. cleanser, moisturizer) or maximum price. 

Youtube Video: [CS50 Final Project: GlowGuide](https://www.youtube.com/watch?v=MsWHJcL2K7g)