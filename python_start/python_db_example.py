#!/usr/bin/env python3
import mysql.connector
from tabulate import tabulate
import datetime
import sys

def open_database(hostname, user_name, mysql_pw, database_name):
    global conn, cursor
    conn = mysql.connector.connect(
        host=hostname,
        user=user_name,
        password=mysql_pw,
        database=database_name
    )
    cursor = conn.cursor()

def executeSelect(query, params=None):
    if params is None:
        params = ()
    cursor.execute(query, params)
    result = cursor.fetchall()
    print("")
    print("Query Result:")
    print("")
    # Use the cursor description to get header names
    header = [col[0] for col in cursor.description]
    print(tabulate(result, headers=header))
    print("")
    return result

def executeUpdate(query, params=None):
    if params is None:
        params = ()
    cursor.execute(query, params)
    conn.commit()

def close_db():
    cursor.close()
    conn.close()

#option 1
def find_available_copies():
    bookstore_name = input("Enter bookstore name: ").strip()
    city = input("Enter city: ").strip()
    # Find the bookstore record
    query = "SELECT bookstoreID FROM Bookstore WHERE bookstoreName = %s AND city = %s"
    cursor.execute(query, (bookstore_name, city))
    result = cursor.fetchone()
    if not result:
        print(f"\nNo bookstore found with name '{bookstore_name}' in {city}.")
        return
    bookstore_id = result[0]
    
    query = """
        SELECT b.bookName, c.price 
        FROM Copy c 
        JOIN Book b ON c.bookID = b.bookID 
        WHERE c.bookstoreID = %s 
          AND c.copyID NOT IN (SELECT copyID FROM Purchase)
    """
    cursor.execute(query, (bookstore_id,))
    copies = cursor.fetchall()
    if not copies:
        print(f"\nNo available copies found at {bookstore_name} in {city}.")
    else:
        print(f"\nAvailable copies at {bookstore_name} in {city}:")
        print(tabulate(copies, headers=["Book Name", "Price"]))
    print("")

#optino 2

def purchase_copy():
    book_name = input("Enter the book name you want to order: ").strip()
    # Find available copies for the given book
    query = """
        SELECT c.copyID, bs.bookstoreName, bs.city, c.price 
        FROM Copy c 
        JOIN Book b ON c.bookID = b.bookID 
        JOIN Bookstore bs ON c.bookstoreID = bs.bookstoreID 
        WHERE b.bookName = %s 
          AND c.copyID NOT IN (SELECT copyID FROM Purchase)
    """
    cursor.execute(query, (book_name,))
    available_copies = cursor.fetchall()
    if not available_copies:
        print("\nThis book is not available.\n")
        return

    print("\nAvailable copies for '{}' are:".format(book_name))
    print(tabulate(available_copies, headers=["Copy ID", "Bookstore Name", "City", "Price"]))
    print("")
    
    try:
        copy_id = int(input("Enter the copyID you want to purchase: ").strip())
    except ValueError:
        print("Invalid copyID. Aborting purchase.\n")
        return

    # Validate
    if not any(copy_id == row[0] for row in available_copies):
        print("Invalid copyID selected. Aborting purchase.\n")
        return

    # Generate new purchaseID
    cursor.execute("SELECT MAX(purchaseID) FROM Purchase")
    max_id = cursor.fetchone()[0]
    new_purchase_id = 0 if max_id is None else max_id + 1

    now = datetime.datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M:%S")
    
    # Insert the purchase record
    query = "INSERT INTO Purchase (purchaseID, copyID, date, time) VALUES (%s, %s, %s, %s)"
    executeUpdate(query, (new_purchase_id, copy_id, date_str, time_str))
    print("Purchase successful!\n")

#option 3

def list_purchases():
    bookstore_name = input("Enter bookstore name: ").strip()
    city = input("Enter city: ").strip()
    # Find the bookstore record
    query = "SELECT bookstoreID FROM Bookstore WHERE bookstoreName = %s AND city = %s"
    cursor.execute(query, (bookstore_name, city))
    result = cursor.fetchone()
    if not result:
        print(f"\nNo bookstore found with name '{bookstore_name}' in {city}.\n")
        return
    bookstore_id = result[0]
    
    query = """
        SELECT b.bookName, c.price, p.date, p.time 
        FROM Purchase p 
        JOIN Copy c ON p.copyID = c.copyID 
        JOIN Book b ON c.bookID = b.bookID 
        WHERE c.bookstoreID = %s
    """
    cursor.execute(query, (bookstore_id,))
    purchases = cursor.fetchall()
    if not purchases:
        print(f"\nNo purchases found for {bookstore_name} in {city}.\n")
    else:
        print(f"\nPurchases for {bookstore_name} in {city}:")
        print(tabulate(purchases, headers=["Book Name", "Price", "Date", "Time"]))
    print("")

#option 4 

def cancel_purchase():
    # Display all purchases
    query = """
        SELECT p.purchaseID, b.bookName, bs.bookstoreName, p.date, p.time 
        FROM Purchase p 
        JOIN Copy c ON p.copyID = c.copyID 
        JOIN Book b ON c.bookID = b.bookID 
        JOIN Bookstore bs ON c.bookstoreID = bs.bookstoreID
    """
    cursor.execute(query)
    purchases = cursor.fetchall()
    if not purchases:
        print("\nNo purchases to cancel.\n")
        return

    print("\nCurrent Purchases:")
    print(tabulate(purchases, headers=["Purchase ID", "Book Name", "Bookstore Name", "Date", "Time"]))
    print("")
    
    try:
        purchase_id = int(input("Enter the purchaseID to cancel: ").strip())
    except ValueError:
        print("Invalid purchaseID.\n")
        return

    # Verify purchase exists
    cursor.execute("SELECT * FROM Purchase WHERE purchaseID = %s", (purchase_id,))
    if not cursor.fetchone():
        print("No purchase found with that ID.\n")
        return

    # Delete the purchase record
    executeUpdate("DELETE FROM Purchase WHERE purchaseID = %s", (purchase_id,))
    print("Purchase cancelled successfully.\n")

#option 5
def add_new_book():
    bookstore_name = input("Enter bookstore name: ").strip()
    city = input("Enter city: ").strip()
    # Verify bookstore exists
    query = "SELECT bookstoreID FROM Bookstore WHERE bookstoreName = %s AND city = %s"
    cursor.execute(query, (bookstore_name, city))
    result = cursor.fetchone()
    if not result:
        print(f"\nNo bookstore found with name '{bookstore_name}' in {city}.\n")
        return
    bookstore_id = result[0]
    
    # Prompt for new book details
    book_name = input("Enter new book name: ").strip()
    author = input("Enter author: ").strip()
    publication_date = input("Enter publication date (YYYY-MM-DD): ").strip()
    book_type = input("Enter type (fic/non): ").strip()
    price_input = input("Enter price: ").strip()
    try:
        price = float(price_input)
    except ValueError:
        print("Invalid price.\n")
        return

    # Generate a new bookID
    cursor.execute("SELECT MAX(bookID) FROM Book")
    max_book_id = cursor.fetchone()[0]
    new_book_id = 0 if max_book_id is None else max_book_id + 1

    # Insert the new book
    query = """
        INSERT INTO Book (bookID, bookName, author, publicationDate, type)
        VALUES (%s, %s, %s, %s, %s)
    """
    cursor.execute(query, (new_book_id, book_name, author, publication_date, book_type))

    # Generate a new copyID
    cursor.execute("SELECT MAX(copyID) FROM Copy")
    max_copy_id = cursor.fetchone()[0]
    new_copy_id = 0 if max_copy_id is None else max_copy_id + 1

    # Insert into the Copy table
    query = """
        INSERT INTO Copy (copyID, bookstoreID, bookID, price)
        VALUES (%s, %s, %s, %s)
    """
    cursor.execute(query, (new_copy_id, bookstore_id, new_book_id, price))
    conn.commit()

    print("\nNew book added successfully!")
    print("\nUpdated Book Table:")
    executeSelect("SELECT * FROM Book")
    print("Updated Copy Table:")
    executeSelect("SELECT * FROM Copy")

#option 6
def quit_program():
    close_db()
    print("Disconnected from database.")
    sys.exit(0)


def main():
    mysql_username = 'thp004'       # change to your MySQL username
    mysql_password = 'Sheek7Ei'   # change to your MySQL password
    database_name = mysql_username  # assuming database name is the same as username

    # Open the database connection
    open_database('localhost', mysql_username, mysql_password, database_name)

    while True:
        print("\nMenu of operations:")
        print("1) Find all available copies at a given bookstore")
        print("2) Purchase an available copy from a particular bookstore")
        print("3) List all purchases for a particular bookstore")
        print("4) Cancel a purchase")
        print("5) Add a new book for a bookstore")
        print("6) Quit")
        choice = input("Enter your choice: ").strip()

        if choice == "1":
            find_available_copies()
        elif choice == "2":
            purchase_copy()
        elif choice == "3":
            list_purchases()
        elif choice == "4":
            cancel_purchase()
        elif choice == "5":
            add_new_book()
        elif choice == "6":
            quit_program()
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
