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


@app.route('/')
def render_home():
    con = get_database(database)
    query = "SELECT englishword, tereoword FROM words"
    cur = con.cursor()
    cur.execute(query)
    langwords = cur.fetchall()
    con.close()
    return render_template('home.html', words=langwords)


if __name__ == '__main__':
    app.run()
