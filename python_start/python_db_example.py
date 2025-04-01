#   DO:  more $HOME/.my.cnf to see your MySQL username and  password
#  CHANGE:  MYUSERNAME and MYMYSQLPASSWORD in the test section of
#  this program to your username and mysql password
#  RUN: ./runpython.sh

import mysql.connector
from tabulate import tabulate


def open_database(hostname, user_name, mysql_pw, database_name):
    global conn
    conn = mysql.connector.connect(host=hostname,
                                   user=user_name,
                                   password=mysql_pw,
                                   database=database_name
                                   )
    global cursor
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


def executeSelect(query):
    cursor.execute(query)
    printFormat(cursor.fetchall())


def insert(table, values):
    query = "INSERT into " + table + " values (" + values + ")" + ';'
    cursor.execute(query)
    conn.commit()


def executeUpdate(query):  # use this function for delete and update
    cursor.execute(query)
    conn.commit()


def close_db():  # use this function to close db
    cursor.close()
    conn.close()


##### Test #######
mysql_username = 'MYUSERNAME'  # please change to your username
mysql_password = 'MYMYSQLPASSWORD'  # please change to your MySQL password

open_database('localhost', mysql_username, mysql_password,
              mysql_username)  # open database

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

