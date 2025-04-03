#   DO:  more $HOME/.my.cnf to see your MySQL username and  password
#  CHANGE:  MYUSERNAME and MYMYSQLPASSWORD in the test section of
#  this program to your username and mysql password
#  RUN: ./runpython.sh

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

def printFormat(result):
    header = []
    for cd in cursor.description:  # get headers
        header.append(cd[0])
    print('')
    print('Query Result:')
    print('')
    print(tabulate(result, headers=header))  # print results in table format

# select and display query


def executeSelect(query, params = None):
    if params is None:
        params = ()
    cursor.execute(query, params)
    result = cursor.fetchall()
    print("")
    print("Query Result:")
    print("")
    #getting header names
    header = [col[0] for col in cursor.description]
    print(tabulate(result, headers = header))
    print("")
    return result


def insert(table, values):
    query = "INSERT into " + table + " values (" + values + ")" + ';'
    cursor.execute(query)
    conn.commit()


def executeUpdate(query, params=None):  # use this function for delete and update
    if params is None:
        params = ()
    cursor.execute(query, params)
    conn.commit()


def close_db():  # use this function to close db
    cursor.close()
    conn.close()

#option 1 stuff
def find_available_copies():
    bookstore_name = input("Enter bookstore name: ").strip()
    city = input("Enter city: ").strip
    query = "SELECT bookstoreID FROM Bookstore WHERE bookstoreName = %s AND city = %s"
    cursor.execute(query, (bookstore_name, city))
    result = cursor.fetchone()
    if not result:
        print(f"\nNo bookstore found with name '{bookstore_name}' in {city}.")
        return
    bookstore_id = result[0]
    #get all availabl ecopies
    query = """
        SELECT b.bookName, c.price
        FROM Copy c
        JOIN Book b ON c.bookID = b.bookID
        WHERE c.bookstoreID = %s
        AND c.copyID NOT IN (SELECT copyID FROM Purchase)
        """
    cursor.execute(query, (bookstore_id))
    copies = cursor.fetchall()
    if not copies:
        print(f"\nNO copies found at {bookstore_name} in {city}.")
    else:
        print(f"\nAvailable copies at {bookstore_name} in {city}:")
        print(tabulate(copies, headers=["Book Name", "Price"]))
        print("")

#Option 2 stuff
def purchase_copy():
    book_name = input("Enter the book name you want to order: ").strip()
    query = """
        SELECT c.copyID, bs.bookstoreName, bs.city, c.price
        FROM Copy c
        JOIN Book b ON c.bookID = b.bookID
        JOIN Bookstore bs ON c.bookstoreID = bs.bookstoreID
        WHERE b.bookName = %s
        AND c.cipyID NOT IN (SELECT copyID FROM Purchase)
        """
    cursor.execute(query, (book_name,))
    available_copies = cursor.fetchall()
    if not available_copies:
        print("\nThis book isn't avaibale. \n")
        return
    print("\nAvailable copies for '{}' are:".format(book_name))
    print(tabulate(available_copies, headers=["Copy ID", "Bookstore Name", "City", "Price"]))
    print("")

    try:
        copy_id = int(input("Enter the copyID you want to purchase: ").strip())
    except ValueError:
        print("Invalid copyID. \n")
        return
    
    #verify if the selcted copyID is among available copies
    if not any(copy_id == row[0] for row in available_copies):
        print("Invalid copyID selected. Abort purchase.\n")
        return
    #new purchase id
    cursor.execute("SELECT MAX(purchaseID) FROM Purchase")
    max_id = cursor.fetchone()[0]
    new_purchase_id = 0 if max_id is None else max_id + 1

    now = datetime.datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M:%S")

    #insert purchase record
    query = "INSERT INTO Purcahse (purchaseID, copyID, date, time) VALUES (%s, %s, %s, %s)"
    executeUpdate(query, (new_purchase_id, copy_id, date_str, time_str))
    print("Purchase successful\n")

#option 3 stuff
def list_purchases():
    bookstore_name = input("Enter bookstore name: ").strip()
    city = input("Enter city: ").strip()
    #find the book store record
    query = "SELECT bookstoreID FROM Bookstore WHERE bookstoreName = %s AND city = %s"
    cursor.execute(query, (bookstore_name, city))
    result = cursor.fetchone()
    if not result:
        print(f"\nNo bookstore found with name {bookstore_name} in {city}")
        return
    bookstore_id = result[0]

    query = """
        SELECT b.bookName, c.price, p,date, p.time
        FROM Purchase p
        JOIN Copy c ON p.copyID = c.copyID
        JOIN Book b ON c.bookID = b.bookID
        WHERE c.bookstoreID = %s
        """
    cursor.execute(query, (bookstore_id,))
    purchases = cursor.fetchall()
    if not purchases:
        print("f\nNo purchases found for {booksore_name} in {city}.\n")
    else:
        print(f"\nPurchaes for {bookstore_name} in {city}:")
        print(tabulate(purchases, headers=["Book Name", "Price", "Date", "Time"]))
        print("")

#option 4 stuff
def cancel_purchases():
    query = """
        SELEcT p.purchaseID, b.bookName, bs.bookstoreName, p.date, p.time
        FROM Purcahse p
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
    print(tabulate(purchases, headers=["Purcahses ID", "Book Name", "Bookstore Name", "Date", "Time"]))
    print("")

    try:
        purchase_id = int(input("Enter the purcahseID to cancel: ").strip())
    except ValueError:
        print("Invalid purchaseID. \n")
        return
    
    #verify purchase exists
    cursor.execute("SELECT * FROM Purchase WHERE purchaseID = %s", (purchase_id,))
    if not cursor.fetchone():
        print("No purchase found with that ID.\n")
        return
    #delete purchase record
    executeUpdate("DELETE FROM Purchase WHERE purchaseID = %s", (purchase_id,))
    print("Purchase cancelled.\n")

#option 5 stuff

def main():
    
    ##### Test #######
    mysql_username = 'thp004'  # please change to your username
    mysql_password = 'Hoangan2004'  # please change to your MySQL password

    open_database('localhost', mysql_username, mysql_password,
                mysql_username)  # open database
    while True:
        print("1) Find all available copies at a given bookstore\n")
        print("2) Purcahse an available copy from a particular bookstore\n")
        print("3) List all purchases for a particular bookstore\n")
        print("4) Cancel a purchase\n")
        print("5) Add a new book for a bookstore\n")
        print("6) Quit")

        choice = input("Enter choice: ")

        if choice == 1:
            find_available_copies()
        if choice == 2:
            purchase_copy()
        if choice == 3:
            list_purchases()
        if choice == 4:
            cancel_purchases()
       

        

        print(' ')
        print('Testing select: ')
        print('=======================================')
        executeSelect('SELECT * FROM DEPT')

        print(' ')
        print('\nTesting insert of dept MATH:')
        print('=======================================')
        insert("DEPT", "'MATH', 'Mathematics', 309, 'SCEN'")
        executeSelect('SELECT * FROM DEPT WHERE DEPT_CODE = "MATH";')

        print(' ')
        print('\nTesting delete of dept MATH:')
        print('=======================================')
        executeUpdate('DELETE FROM DEPT WHERE DEPT_CODE = "MATH";')
        executeSelect('SELECT * FROM DEPT WHERE DEPT_CODE = "MATH";')

        print(' ')
        print('\nTesting update of professor name :')
        print('=======================================')
        executeSelect("SELECT * FROM PROFESSOR WHERE PROF_ID = 123456;")
        executeUpdate("Update PROFESSOR set PROF_NAME = 'Susan Dyer' WHERE PROF_ID = 123456;")
        executeSelect("SELECT * FROM PROFESSOR WHERE PROF_ID = 123456;")

        close_db()  # close database

