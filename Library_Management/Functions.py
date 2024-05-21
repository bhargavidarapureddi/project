def view_transaction_history():
    with open("transaction_history.txt", 'r') as file:
        for line in file:
            print(line.strip())

def view_user_list():
    with open("user_details.txt", 'r') as file:
        for line in file:
            user_details = line.strip().split(',')
            print(f"Username: {user_details[0]}")

def view_borrowed_books_list():
    with open("borrowed_books.txt", 'r') as file:
        for line in file:
            borrow_details = line.strip().split(',')
            print(f"Book ID: {borrow_details[0]}, User: {borrow_details[1]}")

def add_book():
    book_id = input("Enter book ID: ")
    title = input("Enter book title: ")
    author = input("Enter book author: ")
    genre = input("Enter book genre: ")
    quantity = input("Enter book quantity: ")

    with open("book_details.txt", 'r+') as file:
        lines = file.readlines()
        for i, line in enumerate(lines):
            book_details = line.strip().split(',')
            if book_details[1] == title and book_details[2] == author and book_details[3] == genre:
                new_quantity = int(book_details[4]) + int(quantity)
                lines[i] = f"{book_details[0]},{title},{author},{genre},{new_quantity}\n"
                file.seek(0)
                file.writelines(lines)
                print("Book quantity updated successfully.")
                break
        else:
            file.write(f"{book_id},{title},{author},{genre},{quantity}\n")
            print("New book added successfully.")

def update_book():
    book_id = input("Enter book ID to update: ")
    with open("book_details.txt", 'r') as file:
        lines = file.readlines()
    found = False
    with open("book_details.txt", 'w') as file:
        for line in lines:
            book_details = line.strip().split(',')
            if book_details[0] == book_id:
                title = input(f"Enter new title for book ID {book_id}: ")
                author = input(f"Enter new author for book ID {book_id}: ")
                genre = input(f"Enter new genre for book ID {book_id}: ")
                quantity = input(f"Enter new quantity for book ID {book_id}: ")
                new_line = f"{book_id},{title},{author},{genre},{quantity}\n"
                file.write(new_line)
                print("Book updated successfully.")
                found = True
            else:
                file.write(line)
    if not found:
        print("Book ID not found.")

def remove_book():
    book_id = input("Enter book ID to remove: ")
    with open("book_details.txt", 'r') as file:
        lines = file.readlines()
    found = False
    with open("book_details.txt", 'w') as file:
        for line in lines:
            book_details = line.strip().split(',')
            if book_details[0] == book_id:
                print(f"Book ID {book_id}: '{book_details[1]}' by {book_details[2]} removed successfully.")
                found = True
            else:
                file.write(line)
    if not found:
        print("Book ID not found.")

def search_books():
    search_term = input("Enter search term (book name, author, or genre): ").lower()
    found = False
    with open("book_details.txt", 'r') as file:
        for line in file:
            book_details = line.strip().split(',')
            if (search_term in book_details[1].lower()) or (search_term in book_details[2].lower()) or (search_term in book_details[3].lower()):
                print(f"Book ID: {book_details[0]}, Title: {book_details[1]}, Author: {book_details[2]}, Genre: {book_details[3]}, Quantity: {book_details[4]}")
                found = True
    if not found:
        print("No books found matching the search term.")

def borrow_book(username):
    book_id = input("Enter the book ID to borrow: ")
    with open("book_details.txt", 'r+') as file:
        lines = [line.strip().split(',') for line in file]
        for i, book_details in enumerate(lines):
            if book_details[0] == book_id and int(book_details[4]) > 0:
                lines[i][4] = str(int(lines[i][4]) - 1)
                file.seek(0)
                file.truncate()
                file.write('\n'.join([','.join(book) for book in lines]))
                with open("borrowed_books.txt", 'a') as borrow_file:
                    borrow_file.write(f"{book_id},{username}\n")
                print("Book borrowed successfully.")
                break
        else:
            print("Book ID not found or out of stock.")

def return_book(username, late_fee_rate):
    book_id = input("Enter the book ID to return: ")
    with open("borrowed_books.txt", 'r') as borrow_file:
        lines = [line.strip().split(',') for line in borrow_file]
    for i, borrow_details in enumerate(lines):
        if borrow_details[0] == book_id and borrow_details[1] == username:
            with open("book_details.txt", 'r+') as file:
                book_lines = [line.strip().split(',') for line in file]
                for j, book_details in enumerate(book_lines):
                    if book_details[0] == book_id:
                        days_overdue = max(0, int(input("Enter the number of days overdue: ")))
                        late_fee = late_fee_rate * days_overdue
                        print(f"Late fee: Rs{late_fee:.2f}")
                        book_lines[j][4] = str(int(book_lines[j][4]) + 1)
                        file.seek(0)
                        file.truncate()
                        file.write('\n'.join([','.join(book) for book in book_lines]))
                        break
            del lines[i]
            with open("borrowed_books.txt", 'w') as borrow_file:
                borrow_file.write('\n'.join([','.join(borrow) for borrow in lines]))
            with open("transaction_history.txt", 'a') as transaction_file:
                transaction_file.write(f"{book_id},{username},{late_fee}\n")
            print("Book returned successfully.")
            break
    else:
        print("Book ID not found in your borrowed books list.")

        late_fee_rate = 2

