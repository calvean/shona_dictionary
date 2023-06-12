#!/usr/bin/python3
""" DB Module """
import mysql.connector

def create_mysql_database():
    try:
        """ Connect to MySQL server """
        db_connection = mysql.connector.connect(
            host="localhost",
            user="dev",
            password="password"
        )
        cursor = db_connection.cursor()

        """ Create the database """
        cursor.execute("CREATE DATABASE IF NOT EXISTS shona_dict")
        cursor.execute("USE shona_dict")

        """ Create the words table """
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS words (
                id INT AUTO_INCREMENT PRIMARY KEY,
                word VARCHAR(50),
                pronunciation VARCHAR(100),
                audio_url VARCHAR(255),
                word_class_id INT,
                etymology TEXT
            )
        """)

        """ Create the word_classes table """
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS word_classes (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(20)
            )
        """)

        """ Create the meanings table """
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS meanings (
                id INT AUTO_INCREMENT PRIMARY KEY,
                word_id INT,
                meaning TEXT,
                FOREIGN KEY (word_id) REFERENCES words(id)
            )
        """)

        """ Create the synonyms table """
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS synonyms (
                id INT AUTO_INCREMENT PRIMARY KEY,
                word_id INT,
                synonym VARCHAR(50),
                FOREIGN KEY (word_id) REFERENCES words(id)
            )
        """)

        """ Create the antonyms table """
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS antonyms (
                id INT AUTO_INCREMENT PRIMARY KEY,
                word_id INT,
                antonym VARCHAR(50),
                FOREIGN KEY (word_id) REFERENCES words(id)
            )
        """)

        """ Commit changes and close connection """
        db_connection.commit()
        cursor.close()
        db_connection.close()

        print("MySQL database created successfully.")
    
    except mysql.connector.Error as error:
        print("Error creating MySQL database:", error)
