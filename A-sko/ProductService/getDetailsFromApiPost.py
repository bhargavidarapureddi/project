# IMPORTS
from flask import Flask, request, jsonify, Blueprint
import snowflake.connector
from login.login.config import SNOWFLAKE
#-----------------------------------------------------------------------------------------------------
add_products_api = Blueprint('add_products_api', __name__)
#-----------------------------------------------------------------------------------------------------

# API FOR HOME - /aboutOfA-sko
@add_products_api.route('/aboutOfA-sko', methods=['GET'])
def home():
    info = """
                <h1>Welcome to World of A-SKO!</h1>
                <p>Welcome to our A-SKO Fashion Store, where style transcends age! Explore a diverse range of fashion styles for babies, teens, and adults. From trendy teen streetwear to sophisticated adult ensembles, we've got something for everyone. Login to unlock exclusive features and personalized recommendations. Dive into the world of fashion with style guides and trend forecasts. Join us on a stylish adventure where age is just a number, and fashion is timeless.</p> 
            """
    return info

# API FOR POSTMAN TO POST A NEW PRODUCT - /post_data
@add_products_api.route('/post_data', methods=['POST'])
def post_data():
    new_item = request.json
    new_adding_data_from_api = []
    new_adding_data_from_api.append(new_item)
    try:
        connection = snowflake.connector.connect(**SNOWFLAKE)
        cursor = connection.cursor()

        for item in new_adding_data_from_api:
            print("Processing item:", item)
            id_value = item.get('ID')  
            print("ID value:", id_value)
            cursor.execute("""
            INSERT INTO PRODUCTS (ID, title, price, description, image, rating, available,  age, gender)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (item.get('ID'), item.get('title'), item.get('price'), item.get('description'), item.get('image_url'),
                  item.get('rating'), item.get('available'), item.get('age'), item.get('gender')))
        connection.commit()
        cursor.close()
        connection.close()
        return "Data inserted successfully."

    except Exception as e:
        print("Error:", e)  # Print the actual error message for debugging
        return "Error inserting data."


