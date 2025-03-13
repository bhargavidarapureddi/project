from flask import Flask, render_template, redirect, url_for, Blueprint, request, flash
import snowflake.connector
import sys
sys.path.append(r"C:\Users\1038585\Practise\gitApp\A-sko\A-sko\ProductService")
from ProductService.products import get_cart

snowflake_config = {
    'account': 'vccevuc-sa96036',
    'user': 'keerthanjj',
    'password': 'Mypwsnow123@',
    'database': 'ESKO',
    'schema': 'PUBLIC'
}
order_api = Blueprint("order_api", __name__)
order_api.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
row_data =[]
def get_connection():
    try:
        # ** is used to unpack the dictionary
        return snowflake.connector.connect(**snowflake_config)
    except Exception as e:
        print("An error occurred while connecting to Snowflake:", e)
        return None

def get_username(user_email):
    user_email = str(user_email)
    connection = get_connection()
    if connection:
        try:
            cursor = connection.cursor()
            query = f"SELECT USERNAME FROM ESKO.PUBLIC.USERS WHERE EMAIL = '{user_email}';"
            cursor.execute(query)
            username = cursor.fetchone()
            connection.commit()
            connection.close()
            print(type(username))
            return username[0]
        except Exception as e:
            return f"An unexpected error occurred. Please try again later.', {e}"
    


form_data =[] 
@order_api.route('/placeOrder', methods = ["GET","POST"])
def place_order():
    
    if request.method == "POST":
        user_email = request.form['user_email']
        phone = request.form['phone']
        pincode = request.form['pincode']
        flatnumber = request.form['flatnumber']
        city = request.form['city']
        state = request.form['state']
        country = request.form['country']
        connection = get_connection()
        if connection:
            try:
                cursor = connection.cursor()
                query1 = f"UPDATE ESKO.PUBLIC.USERS SET PINCODE = {pincode}, FLAT_NUMBER = '{flatnumber}', STATE ='{state}', COUNTRY = '{country}' WHERE EMAIL = '{user_email}';"
                cursor.execute(query1)
                connection.commit()
                connection.close()
            except Exception as e:
                flash(f'An unexpected error occurred. Please try again later.', 'danger')

        # Append the data to the array
        username = get_username(user_email)
        form_data.append({'username': username, "phone":phone, 'pincode': pincode, 'flatnumber': flatnumber, "city": city, 'state': state, 'country': country})
        print(form_data)
    return render_template('placeorder.html', form_data = form_data)

@order_api.route('/payments')
def payments():

    return render_template('payments.html')

@order_api.route('/orderdetails', methods = ['POST'])
def orderdetails():
    global row_data
    row_data=[]
    if request.method == 'POST':
        for index in range(len(request.form)):
            data_key = f'data_{index}'
            if data_key in request.form:
                row_data.append(request.form[data_key])
        print(row_data)
        cart_contents = get_cart()
        print(cart_contents)
        total_amount = 0
        for item in cart_contents:
            total_amount += (float(item[2]))*(float(item[9]))
        return render_template('orderdetails.html', row_data=row_data, cart_contents=cart_contents, total_amount=total_amount)

@order_api.route('/orderHistory')
def orderHistory():
    print(row_data)
    cart_contents = get_cart()
    print(cart_contents)
    total_amount = 0
    for item in cart_contents:
        total_amount += (float(item[2]))*(float(item[9]))
    return render_template('orderHistory.html', row_data=row_data, cart_contents=cart_contents, total_amount=total_amount)
