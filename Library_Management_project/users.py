from flask import Flask, request, jsonify, session, Blueprint
from config import SNOWFLAKE_CONNECTOR
from datetime import datetime, timedelta

users_api = Blueprint('users_api', __name__)

conn = SNOWFLAKE_CONNECTOR
def user_exists(username):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
    user = cursor.fetchone()
    cursor.close()
    return user is not None

@users_api.route('/user/signup', methods=['POST'])
def user_signup():
    data = request.get_json()
    username = data['username']
    password = data['password']
    
    if user_exists(username):
        return jsonify({'message': 'User with this username already exists'}), 400
    
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
    conn.commit()
    cursor.close()
    
    return jsonify({'message': 'User signed up successfully'}), 200

@users_api.route('/user/signin', methods=['GET'])
def user_signin():
    data = request.get_json()
    username = data['username']
    password = data['password']
    
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
    user = cursor.fetchone()
    cursor.close()
    
    if user:
        session['username'] = username
        return jsonify({'message': 'User signed in successfully'}), 200
    else:
        return jsonify({'message': 'Invalid username or password'}), 401

def is_user_signed_in():
    return 'username' in session

@users_api.route('/user/BOOK_DETAILS', methods=['GET'])
def view_all_BOOK_DETAILS():
    if not is_user_signed_in():
        return jsonify({'message': 'user not signed in'}), 401
    
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM LMS.PUBLIC.BOOK_DETAILS")
    BOOK_DETAILS = cursor.fetchall()
    cursor.close()
    
    return jsonify({'BOOK_DETAILS': BOOK_DETAILS}), 200

@users_api.route('/search', methods=['GET'])
def search_BOOK_DETAILS():
    book_name = request.args.get("BOOK_NAME")
    book_genre = request.args.get("GENRE")
    print(request.args.get("GENRE"))
    book_author = request.args.get("AUTHOR NAME")

    sql_query = "SELECT * FROM BOOK_DETAILS WHERE"
    parameters = []

    if book_name:
        sql_query += " BOOK_NAME LIKE %s"
        parameters.append('%' + book_name + '%')
        
    if book_author:
        sql_query += " AUTHOR LIKE %s"
        parameters.append('%' + book_author + '%')
    if book_genre:
        print(book_genre)
        sql_query += " GENRE LIKE %s"
        print(sql_query) 
        parameters.append('%' + book_genre + '%')
        

    sql_query += " LIMIT 1"

    cursor = conn.cursor()
    cursor.execute(sql_query, parameters)
    book = cursor.fetchone()
    cursor.close()

    if book:
        return jsonify({'BOOK_DETAILS': book}), 200
    else:
        return jsonify({'message': 'No book found'}), 404

@users_api.route('/borrow', methods=['POST'])
def borrow_book():
    if not is_user_signed_in():  
        return jsonify({'message': 'User not signed in'}), 401
    
    data = request.get_json()
    
    book_id = data.get('book_id')
    username = session.get('username')
    
    if book_id is None or username is None:
        return jsonify({'message': 'Missing book_id or username'}), 400
    
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT QUANTITY FROM BOOK_DETAILS WHERE BOOK_ID = %s", (book_id,))
        book = cursor.fetchone()
        if not book or book[0] <= 0:
            return jsonify({'message': 'Book not available'}), 400
        
        cursor.execute("SELECT COUNT(*) FROM BORROWED_BOOKS WHERE USERNAME = %s", (username,))
        borrow_count = cursor.fetchone()[0]
        if borrow_count >= 3:
            return jsonify({'message': 'You have borrowed the maximum number of books allowed'}), 400
        
        borrow_date = datetime.now()
        
        cursor.execute("INSERT INTO BORROWED_BOOKS (USERNAME, BOOK_ID, BORROW_DATE) VALUES (%s, %s, %s)",
                       (username, book_id, borrow_date))
        
        cursor.execute("UPDATE BOOK_DETAILS SET QUANTITY = QUANTITY - 1 WHERE BOOK_ID = %s", (book_id,))
        
        conn.commit()
        
        return jsonify({'message': 'Book borrowed successfully'}), 200
    
    except Exception as e:
        conn.rollback()
        return jsonify({'message': 'Error borrowing book', 'error': str(e)}), 500
    
    finally:
        cursor.close()

@users_api.route('/return', methods=['POST'])
def return_book():
    if not is_user_signed_in():
        return jsonify({'message': 'User not signed in'}), 401
    
    data = request.get_json()
    book_id = data.get('book_id')
    username = session.get('username')
    
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM BORROWED_BOOKS WHERE USERNAME = %s AND BOOK_ID = %s", (username, book_id))
    borrowing = cursor.fetchone()

    if not borrowing:
       return jsonify({'message': 'You have not borrowed this book'}), 400

    return_date = borrowing[3]

    if return_date is not None:
        overdue_days = (datetime.now() - return_date).days
    else:
        overdue_days = 0

    cursor.execute("UPDATE BORROWED_BOOKS SET RETURN_DATE = %s WHERE USERNAME = %s AND BOOK_ID = %s",
               (datetime.now(), username, book_id))

    cursor.execute("UPDATE BOOK_DETAILS SET QUANTITY = QUANTITY + 1 WHERE BOOK_ID = %s", (book_id,))

    conn.commit()
    cursor.close()

    if overdue_days > 0:
        return jsonify({'message': 'Book returned successfully. You have overdue of {} days'.format(overdue_days)}), 200
    else:
        return jsonify({'message': 'Book returned successfully'}), 200
