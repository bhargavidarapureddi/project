# IMPORTS
from flask import Flask, render_template, session, redirect, url_for, request, Blueprint
import snowflake.connector
from login.login.config import SNOWFLAKE

#-----------------------------------------------------------------------------------------------------

# BLUEPRINT TO USE IT IN LOGIN / APP
products_api = Blueprint('products_api', __name__)
# SECRET KEY FOR SESSION
products_api.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

#-----------------------------------------------------------------------------------------------------

# TO ESTABLISH CONNECTION PYTHON TO SNOWFLAKE
def get_connection():
    try:
        # ** is used to unpack the dictionary
        return snowflake.connector.connect(**SNOWFLAKE)
    except Exception as e:
        print("An error occurred while connecting to Snowflake:", e)
        return None

# SEARCH AND GET PRODUCTS BASED ON AGE CATEGORY
def get_products(age_category=None, page=1, per_page=10):
    products = []
    total_count = 0
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor()
            query = "SELECT * FROM ESKO.PUBLIC.PRODUCTS"
            if age_category:
                # used string concatinate
                if age_category == 'below_10':
                    query += " WHERE AGE < 10"
                elif age_category == '10_to_20':
                    query += " WHERE AGE BETWEEN 10 AND 20"
                elif age_category == 'above_20':
                    query += " WHERE AGE > 20"
            cursor.execute(query)
            total_products = cursor.fetchall()
            total_count = len(total_products)
            products = total_products[(page - 1) * per_page: page * per_page]
        except Exception as e:
            print("An error occurred while fetching product data:", e)
        finally:
            cursor.close()
            conn.close()
    return products, total_count

# SEARCH BY PRODUCT NAME
def get_product_by_name(title):
    product = None
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM PUBLIC.PRODUCTS WHERE title = %s", (title,))
            # used fetchone() to get only one from the base
            product = cursor.fetchone()
        except Exception as e:
            print("An error occurred while fetching product by title:", e)
        finally:
            cursor.close()
            conn.close()
    return product

# ADD PRODUCT TO CART AND UPDATE A QUANTITY 
def add_to_cart(title):
    product = get_product_by_name(title)
    if product:
        if 'cart' not in session:
            session['cart'] = []

        # check if the product is already in the cart
        for item in session['cart']:
            if item[1] == title:
                # if it is, increment the quantity and exit the function
                item[9] += 1
                item[6] -= 1
                session.modified = True
                print("Product quantity increased in cart:", title)
                return

        # If the product is not in the cart, add it with a quantity of 1
        product_with_quantity = list(product)
        product_with_quantity.append(1)  # Quantity of the product
        session['cart'].append(product_with_quantity)
        session.modified = True
        print("Product added to cart:", title)


# REMOVE A PRODUCT FROM CART AND DECREMENT THE QUANTITY IF MANY
def remove_from_cart(title):
    if 'cart' in session:
        cart = session['cart']
        # USED ENUMARATE TO COUNT THE DUPLICATES
        for i, item in enumerate(cart):
            if item[1] == title:
                if item[9] > 1:
                    item[9] -= 1
                    item[6] += 1
                else:  
                    # If quantity is already 0 or less, remove the item from the cart
                    del cart[i]
                    # Exit the loop after removing one instance of the product
                    break  
        # Update the cart in the session
        session['cart'] = cart
        # Mark the session as modified  
        session.modified = True  


def get_cart():
    return session.get('cart', [])

# SEARCH AND GET PRODUCTS BASED ON TITLE
def get_products_by_query(query):
    products = []
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM PUBLIC.PRODUCTS WHERE title LIKE %s", ('%' + query + '%',))
            products = cursor.fetchall()
        except Exception as e:
            print("An error occurred while fetching product data:", e)
        finally:
            cursor.close()
            conn.close()
    return products

#-----------------------------------------------------------------------------------------------------

# API TO DISPLAY THE PRODUCTS - /displayProducts
@products_api.route('/displayProducts')
def index():
    # check page in html - if not make page default value is 1
    page = request.args.get('page', default=1, type=int)
    # Retrieve age category from query parameters
    age_category = request.args.get('age_category')  
    products, total_count = get_products(age_category=age_category, page=page)
    # Number of products per page
    per_page = 10 
    # Number of pagesrequired to display all products
    total_pages = (total_count + per_page - 1) // per_page
    return render_template('index.html', products=products, page=page, total_pages=total_pages)

# API WHICH ACCEPTS STRING "TITLE" - /product/<string:title>
@products_api.route('/product/<string:title>')
def product(title):
    product = get_product_by_name(title)
    return render_template('product.html', product=product)

#API WHICH ADDS A PRODUCT BY NAME - /add_to_cart/<string:title>
@products_api.route('/add_to_cart/<string:title>', methods=['POST'])
def add_to_cart_route(title):
    add_to_cart(title)
    return redirect(url_for('.index'))

# API TO REMOVE A PRODUCT FROM CART BY NAME - /remove_from_cart/<string:title>
@products_api.route('/remove_from_cart/<string:title>', methods=['POST'])
def remove_from_cart_route(title):
    remove_from_cart(title)
    return redirect(url_for('.cart'))

# API TO CART - /cart
@products_api.route('/cart')
def cart():
    cart_contents = get_cart()
    print("Cart contents:", cart_contents)
    return render_template('cart.html', cart_contents=cart_contents)

# API FOR SEARCH BAR - /search
@products_api.route('/search')
def search():
    query = request.args.get('query')
    products = get_products_by_query(query)
    page = request.args.get("page", type=int, default=1)
    per_page = 10  # Assuming 10 products per page
    total_count = len(products)
    total_pages = (total_count + per_page - 1) // per_page
    return render_template('index.html', page=page, products=products, total_pages=total_pages)

# ORDER DETAILS NEED TO BE DONE...
@products_api.route('/orderdetails')
def order_details():
    return render_template('orderdetails.html')
#ehen i click on the add cart button in cart bagged para increased by one based on clickings also , remove from cart clicken it should be decremented by one based on clickings and availability
