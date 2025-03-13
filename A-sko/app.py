# IMPORTS
from flask import Flask, render_template, redirect, request, url_for, flash
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
from snowflake.connector import connect  # Import for connection
from werkzeug.security import generate_password_hash, check_password_hash
#-----------------------------------------------------------------------------------------------------------------

from login.login.config import SECRET_KEY,SNOWFLAKE
from login.login.models import User
from ProductService.products import products_api
from ProductService.getDetailsFromApiPost import add_products_api
from OrderService.orders import order_api
#-----------------------------------------------------------------------------------------------------------------

# APP -> FLASK INTIALIZATION


# __package__ = 'login.login'

app = Flask(__name__)
# REGISTERING THE BLUE-PRINTS FROM DIFFERENT FILE 
app.register_blueprint(products_api)

app.register_blueprint(add_products_api)

app.register_blueprint(order_api)


# CONFIGURATION WITH DATABASE (SNOW-FLAKE) WITH CREDENTIALS
app.config['SECRET_KEY'] = SECRET_KEY
app.config['SNOWFLAKE'] = SNOWFLAKE

# instance if LoginManager by Flask-Login : for user Authentication  
login_manager = LoginManager()

# tells Flask-Login to work with Flask : "app"
login_manager.init_app(app)

# view function , user login without Authentication : it redirects to "login"
login_manager.login_view = 'login'

# Loader Function : call back function to reload the user obj in session -: Flask-Login
@login_manager.user_loader
# takes email as a unique identifier
def load_user(email): 
    # User class from models.py 
    return User.get_by_email(email)


#-----------------------------------------------------------------------------------------------------------------

# ROUTES :

app.config


# HOME API - /
@app.route('/')
def home():
    return render_template('welcome.html')

# SINGN UP API - /signup
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']  # Assuming username is still collected for display
        email = request.form['email']
        ph_number = request.form['ph_number']
        password = request.form['password']
        city = request.form['city'] if 'city' in request.form else None

        try:
            # check for exixting mail in database
            if User.get_by_email(email):
                flash('Email address already exists. Please choose another one.', 'danger')
                return render_template('signup.html')

            # Hash password before storing user data
            hashed_password = generate_password_hash(password)

            # insert data in USER table database
            if User.create_user(username, email, ph_number, hashed_password, city):
                flash('Registration Successful!', 'success')
                return redirect(url_for('login'))
            else:
                flash(f'An unexpected error occurred. Please try again later.', 'danger')
        except Exception as e:
            print(f'Error creating user: {str(e)}')  # Log the error for troubleshooting
            flash(f'An unexpected error occurred. Please try again later.', 'danger')

    return render_template('signup.html')

# LOGIN API - /login
@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':
        # getting data from FORM login.html
        email = request.form['email']
        password = request.form['password']

        # check for existing of mail from USER TABLE
        user = User.get_by_email(str(email))  

        if user :
            #decrypts the pass stored in USER TABLE
            if check_password_hash(user.password, password):
                login_user(user,remember=True)

                # redirects to  index using the registered Blueprint 
                # of products : products_api
                return redirect(url_for('products_api.index'))
            else:
               flash('Invalid password, please check again', 'danger') 
        else:
            flash("Sorry, Email does not exist",'danger')
            # redirects to login page
    return render_template('login.html',boolean=True)

# LOGOUT API - /logout
@app.route('/logout')

@login_required
def logout():
    logout_user()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('login'))

if __name__ == '__main__':
    # Run the app in debug mode
    app.run(debug=True)  
