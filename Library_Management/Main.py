import hashlib
from Functions import view_transaction_history, view_user_list, view_borrowed_books_list, add_book, update_book, remove_book, borrow_book, return_book, search_books

LIBRARIAN_FILE = "librarian_details.txt"
USER_FILE = "user_details.txt"
BOOK_FILE = "book_details.txt"
BORROW_FILE = "borrow_details.txt"

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def librarian_signup():
    username = input("Enter librarian username: ")
    password = input("Enter password: ")
    password = input("Enter password again: ")
    with open(LIBRARIAN_FILE, 'a') as file:
        with open(LIBRARIAN_FILE, 'r') as read_file:
            for line in read_file:
                if username == line.strip().split(',')[0]:
                    print("Username already exists. Please choose a different username.")
                    return
        hashed_password = hash_password(password)
        file.write(f"{username},{hashed_password}\n")
    print("Librarian signup successful.")
    librarian_login()

def librarian_login():
    username = input("Enter librarian username: ")
    password = input("Enter password: ")
    with open(LIBRARIAN_FILE, 'r') as file:
        for line in file:
            user, stored_password = line.strip().split(',')
            if user == username:
                if hash_password(password) == stored_password:
                    print(f"Librarian login successful. Welcome back, {username}!")
                    librarian_dashboard(username)
                    return
                else:
                    print("Incorrect password. Please try again.")
                    return
    print("Librarian not found. Please signup first.")

def user_signup():
    username = input("Enter user username: ")
    password = input("Enter password: ")
    password = input("Enter password again: ")
    with open(USER_FILE, 'a') as file:
        with open(USER_FILE, 'r') as read_file:
            for line in read_file:
                if username == line.strip().split(',')[0]:
                    print("Username already exists. Please choose a different username.")
                    return
        hashed_password = hash_password(password)
        file.write(f"{username},{hashed_password}\n")
    print("User signup successful.")
    user_login()

def user_login():
    username = input("Enter user username: ")
    password = input("Enter password: ")
    with open(USER_FILE, 'r') as file:
        for line in file:
            user, stored_password = line.strip().split(',')
            if user == username:
                if hash_password(password) == stored_password:
                    print(f"User login successful. Welcome back, {username}!")
                    user_menu(username)
                    return
                else:
                    print("Incorrect password. Please try again.")
                    return
    print("User not found. Please signup first.")

def librarian_dashboard(username):
    while True:
        print("\n===== LIBRARIAN DASHBOARD =====")
        print("1. Transaction History")
        print("2. User List")
        print("3. Borrowed Books List")
        print("4. All Books")
        print("5. Add Book")
        print("6. Update Book")
        print("7. Remove Book")
        print("8. Logout")
        print("9. Exit")
        choice = input("Enter your choice: ")
        if choice == '1':
            view_transaction_history()
        elif choice == '2':
            view_user_list()
        elif choice == '3':
            view_borrowed_books_list()
        elif choice == '4':
            view_all_books()
        elif choice == '5':
            add_book()
        elif choice == '6':
            update_book()
        elif choice == '7':
            remove_book()  
        elif choice == '8':
            print(f"Goodbye, {username}. You have been successfully logged out.")
        elif choice == '9':
            print("Exit")
            break
        else:
            print("Invalid choice. Please try again.")

def user_menu(username):
    while True:
        print("\n===== USER MENU =====")
        print("1. All Books")
        print("2. Borrow Book")
        print("3. Return Book")
        print("4. Search")
        print("5. Logout")
        print("6. Exit")
        choice = input("Enter your choice: ")
        if choice == '1':
           view_all_books()
        elif choice == '2':
            borrow_book(username)
        elif choice == '3':
            return_book(username,late_fee_rate)
        elif choice == '4':
            search_books()
        elif choice == '5':
            print(f"Goodbye, {username}. You have been successfully logged out.")
            break
        elif choice == '6':
            print("Exit")
            break
        else:
            print("Invalid choice. Please try again.")

def view_all_books():
    print("\n===== ALL BOOKS =====")
    with open(BOOK_FILE, 'r') as file:
        for line in file:
            book_details = line.strip().split(',')
            print(f"Book ID: {book_details[0]}, {book_details[1]}, {book_details[2]}, {book_details[3]}, {book_details[4]}")

def main_menu():
    print("\n===== MAIN MENU =====")
    print("1. Librarian Signup")
    print("2. Librarian Login")
    print("3. User Signup")
    print("4. User Login")
    print("5. Exit")

def main():
    while True:
        main_menu()
        choice = input("Enter your choice: ")
        if choice == '1':
            librarian_signup()
        elif choice == '2':
            librarian_login()
        elif choice == '3':
            user_signup()
        elif choice == '4':
            user_login()
        elif choice == '5':
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")

late_fee_rate = 2           

if __name__ == "__main__":
    main()