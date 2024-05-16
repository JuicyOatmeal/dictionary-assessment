from flask import Flask, render_template
import sqlite3
from sqlite3 import Error, connect

app = Flask(__name__)
database = "C:/Users/20249/OneDrive - Wellington College/13dts/assesmetn/dbs"


def get_database(database_file):
    try:
        returned_db = sqlite3.connect(database_file)
        return returned_db
    except Error as error:
        print(error)


@app.route('/home')
def render_home():
    return render_template('home.html')


@app.route('/all_words')
def render_all_words():
    con = get_database(database)
    query = "SELECT primarykey, englishword, tereoword, category, definition, level FROM words"
    cur = con.cursor()
    cur.execute(query)
    info = cur.fetchall()
    return render_template('all_words.html', words_table=info)


@app.route('/category_list')
def render_category_list():
    con = get_database(database)
    query = "SELECT category FROM words"
    cur = con.cursor()
    cur.execute(query)
    info = cur.fetchall()
    return render_template("category_list.html", category=info)


@app.route('/all_words/word')
def render_word():
    return render_template("word.html")#, word=all)


if __name__ == '__main__':
    app.run()
