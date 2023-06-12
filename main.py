#!/usr/bin/python3
""" main Module """
from db import create_mysql_database
from console import connect_to_database, load_dictionary_data, display_menu, lookup_word, add_word, delete_word

import mysql.connector

def main():
    """ Connect to the database """
    connection = connect_to_database()

    """ Load dictionary data """
    dictionary_data = load_dictionary_data(connection)

    """ Check database connection
     and if dictionary data is loaded successfully """
    if not connection or not dictionary_data:
        return

    """" Display the menu and process user input """
    while True:
        display_menu()
        choice = input("Enter your choice: ")

        if choice == '1':
            lookup_word(dictionary_data)
        elif choice == '2':
            add_word(connection, dictionary_data)
        elif choice == '3':
            delete_word(connection, dictionary_data)
        elif choice == '4':
            print("Thank you for using the Dictionary. Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

    """ Close the database connection """
    connection.close()

if __name__ == '__main__':
    main()
