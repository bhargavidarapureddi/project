from flask import Flask, request, jsonify, session, Blueprint
from config import SNOWFLAKE_CONNECTOR
from datetime import datetime, timedelta

librarians_api = Blueprint('librarians_api', __name__)

conn = SNOWFLAKE_CONNECTOR
def librarian_exists(username):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM librarians WHERE username = %s", (username,))
    librarian = cursor.fetchone()
    cursor.close()
    return librarian is not None

@librarians_api.route('/librarian/signup', methods=['POST'])
def librarian_signup():
    data = request.get_json()
    username = data['username']
    password = data['password']
    
    if librarian_exists(username):
        return jsonify({'message': 'Librarian with this username already exists'}), 400
    
    cursor = conn.cursor()
    cursor.execute("INSERT INTO librarians (username, password) VALUES (%s, %s)", (username, password))
    conn.commit()
    cursor.close()
    
    return jsonify({'message': 'Librarian signed up successfully'}), 200

@librarians_api.route('/librarian/signin', methods=['GET'])
def librarian_signin():
    data = request.get_json()
    username = data['username']
    password = data['password']
    
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM librarians WHERE username = %s AND password = %s", (username, password))
    librarian = cursor.fetchone()
    cursor.close()
    
    if librarian:
        session['username'] = username
        return jsonify({'message': 'Librarian signed in successfully'}), 200
    else:
        return jsonify({'message': 'Invalid username or password'}), 401
    
def is_librarian_signed_in():
    return 'username' in session

def is_user_signed_in():
    return 'username' in session
   
@librarians_api.route('/librarian/books', methods=['GET'])
def view_all_books():
    if not is_librarian_signed_in():
        return jsonify({'message': 'Librarian not signed in'}), 401
    
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM LMS.PUBLIC.BOOK_DETAILS")
    books = cursor.fetchall()
    cursor.close()

    return jsonify({'books': books}), 200

@librarians_api.route('/transactions', methods=['GET'])
def view_transaction_history():
    if not is_librarian_signed_in():
        return jsonify({'message': 'Librarian not signed in'}), 401
    
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM TRANSACTIONS")
    transactions = cursor.fetchall()
    cursor.close()
    
    return jsonify({'transactions': transactions}), 200

@librarians_api.route('/borrowed', methods=['GET'])
def view_borrowed_list():
    if not is_user_signed_in():
        return jsonify({'message': 'User not signed in'}), 401
    
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM BORROWED_BOOKS WHERE USERNAME = (SELECT USERNAME FROM USERS WHERE USERNAME = %s)", (session['username'],))
    borrowed_books = cursor.fetchall()
    cursor.close()
    
    return jsonify({'borrowed_books': borrowed_books}), 200

@librarians_api.route('/users', methods=['GET'])
def view_users_list():
    if not is_librarian_signed_in():
        return jsonify({'message': 'Librarian not signed in'}), 401
    
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM USERS")
    users = cursor.fetchall()
    cursor.close()
    
    return jsonify({'users': users}), 200

@librarians_api.route('/book', methods=['POST'])
def add_book():
    
    conn = SNOWFLAKE_CONNECTOR
    cursor = conn.cursor()
    
    data = request.get_json()
    for book_data in data:
        book_name = book_data.get('book_name')
        author = book_data.get('author')
        genre = book_data.get('genre')
        quantity = book_data.get('quantity')

        cursor.execute("SELECT MAX(BOOK_ID) FROM BOOK_DETAILS")
        max_book_id = cursor.fetchone()[0]
        book_id = max_book_id + 1 if max_book_id is not None else 1

        cursor.execute("SELECT * FROM BOOK_DETAILS WHERE BOOK_NAME = %s AND AUTHOR = %s AND GENRE = %s", (book_name, author, genre))
        existing_book = cursor.fetchone()

        if existing_book:
            updated_quantity = int(existing_book[4]) + int(quantity)
            cursor.execute("UPDATE BOOK_DETAILS SET QUANTITY = %s WHERE BOOK_NAME = %s AND AUTHOR = %s AND GENRE = %s",
                           (updated_quantity, book_name, author, genre))
            return "Book Added"
        else:
            cursor.execute("INSERT INTO BOOK_DETAILS (BOOK_ID, BOOK_NAME, AUTHOR, GENRE, QUANTITY) VALUES (%s, %s, %s, %s, %s)",
                           (book_id, book_name, author, genre, quantity))
            return "Book Added"
    
    conn.commit()
    cursor.close()
    conn.close()

@librarians_api.route('/updatebooks/<int:book_id>', methods=['PUT'])
def update_book(book_id):
    # if not is_librarian_signed_in():
    #     return jsonify({'message': 'Librarian not signed in'}), 401
    
    data = request.get_json()
    title = data.get('book_name')
    author = data.get('author')
    genre = data.get('genre')
    quantity = data.get('quantity')
    
    cursor = conn.cursor()
    if title:
        print("in title")
        cursor.execute("UPDATE BOOK_DETAILS SET BOOK_NAME = %s WHERE BOOK_ID = %s", (title, book_id))
    if author:
        print("author")
        cursor.execute("UPDATE BOOK_DETAILS SET AUTHOR = %s WHERE BOOK_ID = %s", (author, book_id))
    if genre:
        print("genre")
        cursor.execute("UPDATE BOOK_DETAILS SET genre = %s WHERE BOOK_ID = %s", (genre, book_id))
    if quantity:
        print("quantity")
        cursor.execute("UPDATE BOOK_DETAILS SET QUANTITY = %s WHERE BOOK_ID = %s", (quantity, book_id))
    
    conn.commit()
    cursor.close()
    
    return jsonify({'message': 'Book updated successfully'}), 200

@librarians_api.route('/deletebooks/<int:book_id>', methods=['DELETE'])
def remove_book(book_id):
    if not is_librarian_signed_in():
        return jsonify({'message': 'Librarian not signed in'}), 401
    
    cursor = conn.cursor()
    cursor.execute("DELETE FROM BOOK_DETAILS WHERE BOOK_ID = %s", (book_id,))
    conn.commit()
    cursor.close()
    
    return jsonify({'message': 'Book removed successfully'}), 200

def calculate_overdue_days(return_date):
    return max((datetime.now() - return_date).days, 0)

if __name__ == '__main__':
    librarians_api.run(debug=True)
