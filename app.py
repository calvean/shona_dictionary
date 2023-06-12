#!/usr/bin/python3
""" Flask Module """
from flask import Flask, render_template, request, flash, redirect
import mysql.connector
from console import connect_to_database, load_dictionary_data
from werkzeug.utils import secure_filename
import os


UPLOAD_FOLDER = 'static/speach'

app = Flask(__name__)
app.secret_key = 'secret_key'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

connection = None
dictionary_data = {}

ALLOWED_EXTENSIONS = {'mp3', 'wav'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def upload_file(audio_file):
    if audio_file:
        if audio_file and allowed_file(audio_file.filename):
            filename = secure_filename(audio_file.filename)
            audio_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return filename
    return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/lookup', methods=['GET', 'POST'])
def lookup():
    if request.method == 'POST':
        word = request.form['word']
        if word in dictionary_data:
            word_data = dictionary_data[word]
            return render_template('lookup.html', word_data=word_data)
        else:
            return render_template('lookup.html', error='Word not found in the dictionary.')
    return render_template('lookup.html')

@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        word = request.form['word']
        pronunciation = request.form['pronunciation']
        word_class_name = request.form['word_class']
        etymology = request.form['etymology']
        meanings = request.form.getlist('meanings')
        synonyms = request.form.getlist('synonyms')
        antonyms = request.form.getlist('antonyms')

        audio_file = request.files['audio']
        audio_url = upload_file(audio_file)

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

            cursor.close()
            connection.commit()

            return render_template('add.html', success='Word added successfully.')

        except mysql.connector.Error as error:
            print("Error adding word:", error)

    return render_template('add.html')


@app.route('/delete', methods=['GET', 'POST'])
def delete():
    if request.method == 'POST':
        word = request.form['word']

        if word not in dictionary_data:
            return render_template('delete.html', error='Word not found in the dictionary.')

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

            cursor.close()
            connection.commit()

            return render_template('delete.html', success='Word deleted successfully.')

        except mysql.connector.Error as error:
            print("Error deleting word:", error)

    return render_template('delete.html')

if __name__ == '__main__':
    connection = connect_to_database()
    dictionary_data = load_dictionary_data(connection)
    app.run(debug=True)

