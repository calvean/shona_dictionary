#!/usr/bin/python3
""" Console Module """
import mysql.connector

def connect_to_database():
    try:
        """ Connect to MySQL server """
        db_connection = mysql.connector.connect(
            host="localhost",
            user="dev",
            password="password",
            database="shona_dict"
        )
        return db_connection

    except mysql.connector.Error as error:
        print("Error connecting to the database:", error)
        return None


def load_dictionary_data(connection):
    dictionary_data = {}

    if connection:
        try:
            cursor = connection.cursor()

            """ Retrieve word classes """
            cursor.execute("SELECT * FROM word_classes")
            word_classes = cursor.fetchall()
            dictionary_data['word_classes'] = {word_class[0]: word_class[1] for word_class in word_classes}

            """ Retrieve words """
            cursor.execute("SELECT * FROM words")
            words = cursor.fetchall()

            for word in words:
                word_id = word[0]
                word_data = {
                    'word': word[1],
                    'pronunciation': word[2],
                    'audio_url': word[3],
                    'word_class': dictionary_data['word_classes'].get(word[4]),
                    'etymology': word[5],
                    'meanings': [],
                    'synonyms': [],
                    'antonyms': []
                }

                """ Retrieve meanings """
                cursor.execute("SELECT * FROM meanings WHERE word_id = %s", (word_id,))
                meanings = cursor.fetchall()
                word_data['meanings'] = [meaning[2] for meaning in meanings]

                """ Retrieve synonyms """
                cursor.execute("SELECT * FROM synonyms WHERE word_id = %s", (word_id,))
                synonyms = cursor.fetchall()
                word_data['synonyms'] = [synonym[2] for synonym in synonyms]

                """ Retrieve antonyms """
                cursor.execute("SELECT * FROM antonyms WHERE word_id = %s", (word_id,))
                antonyms = cursor.fetchall()
                word_data['antonyms'] = [antonym[2] for antonym in antonyms]

                dictionary_data[word_data['word']] = word_data

            cursor.close()

        except mysql.connector.Error as error:
            print("Error loading dictionary data:", error)

    return dictionary_data
    
def display_menu():
    print("Welcome to the Dictionary!")
    print("1. Look up a word")
    print("2. Add a word")
    print("3. Delete a word")
    print("4. Quit")


def lookup_word(dictionary_data):
    word = input("Enter the word to look up: ")

    if word in dictionary_data:
        word_data = dictionary_data[word]
        print("Word:", word_data['word'])
        print("Pronunciation:", word_data['pronunciation'])
        print("Meanings:")
        for i, meaning in enumerate(word_data['meanings'], 1):
            print(f"{i}. {meaning}")
        print("Synonyms:", ", ".join(word_data['synonyms']))
        print("Antonyms:", ", ".join(word_data['antonyms']))
    else:
        print("Word not found in the dictionary.")



def add_word(connection, dictionary_data):
    word = input("Enter the new word: ")

    if word in dictionary_data:
        print("Word already exists in the dictionary.")
        return

    pronunciation = input("Enter the pronunciation: ")
    audio_url = input("Enter the audio URL: ")
    word_class_name = input("Enter the word class name: ")
    etymology = input("Enter the etymology: ")

    meanings = []
    while True:
        meaning = input("Enter a meaning (press enter to finish): ")
        if not meaning:
            break
        meanings.append(meaning)

    synonyms = []
    while True:
        synonym = input("Enter a synonym (press enter to finish): ")
        if not synonym:
            break
        synonyms.append(synonym)

    antonyms = []
    while True:
        antonym = input("Enter an antonym (press enter to finish): ")
        if not antonym:
            break
        antonyms.append(antonym)

    try:
        cursor = connection.cursor()

        # Check if the word class exists, or insert a new one
        cursor.execute("SELECT id FROM word_classes WHERE name = %s", (word_class_name,))
        result = cursor.fetchone()
        if result:
            word_class_id = result[0]
        else:
            insert_word_class_query = "INSERT INTO word_classes (name) VALUES (%s)"
            cursor.execute(insert_word_class_query, (word_class_name,))
            word_class_id = cursor.lastrowid

        # Insert word into words table
        insert_word_query = "INSERT INTO words (word, pronunciation, audio_url, word_class_id, etymology) " \
                            "VALUES (%s, %s, %s, %s, %s)"
        word_values = (word, pronunciation, audio_url, word_class_id, etymology)
        cursor.execute(insert_word_query, word_values)
        word_id = cursor.lastrowid

        # Insert meanings into meanings table
        if meanings:
            insert_meaning_query = "INSERT INTO meanings (word_id, meaning) VALUES (%s, %s)"
            meaning_values = [(word_id, meaning) for meaning in meanings]
            cursor.executemany(insert_meaning_query, meaning_values)

        # Insert synonyms into synonyms table
        if synonyms:
            insert_synonym_query = "INSERT INTO synonyms (word_id, synonym) VALUES (%s, %s)"
            synonym_values = [(word_id, synonym) for synonym in synonyms]
            cursor.executemany(insert_synonym_query, synonym_values)

        # Insert antonyms into antonyms table
        if antonyms:
            insert_antonym_query = "INSERT INTO antonyms (word_id, antonym) VALUES (%s, %s)"
            antonym_values = [(word_id, antonym) for antonym in antonyms]
            cursor.executemany(insert_antonym_query, antonym_values)

        # Update dictionary data
        dictionary_data[word] = {
            'word': word,
            'pronunciation': pronunciation,
            'audio_url': audio_url,
            'word_class': word_class_name,
            'etymology': etymology,
            'meanings': meanings,
            'synonyms': synonyms,
            'antonyms': antonyms
        }

        print("Word added successfully.")

        cursor.close()
        connection.commit()

    except mysql.connector.Error as error:
        print("Error adding word:", error)

def delete_word(connection, dictionary_data):
    word = input("Enter the word to delete: ")

    if word not in dictionary_data:
        print("Word not found in the dictionary.")
        return

    try:
        cursor = connection.cursor()

        # Get the word ID
        select_word_id_query = "SELECT id FROM words WHERE word = %s"
        cursor.execute(select_word_id_query, (word,))
        result = cursor.fetchone()
        word_id = result[0]

        # Delete associated antonyms
        delete_antonyms_query = "DELETE FROM antonyms WHERE word_id = %s"
        cursor.execute(delete_antonyms_query, (word_id,))

        # Delete associated synonyms
        delete_synonyms_query = "DELETE FROM synonyms WHERE word_id = %s"
        cursor.execute(delete_synonyms_query, (word_id,))

        # Delete associated meanings
        delete_meanings_query = "DELETE FROM meanings WHERE word_id = %s"
        cursor.execute(delete_meanings_query, (word_id,))

        # Delete word from words table
        delete_word_query = "DELETE FROM words WHERE word = %s"
        cursor.execute(delete_word_query, (word,))

        # Remove word from dictionary data
        del dictionary_data[word]

        print("Word deleted successfully.")

        cursor.close()
        connection.commit()

    except mysql.connector.Error as error:
        print("Error deleting word:", error)


