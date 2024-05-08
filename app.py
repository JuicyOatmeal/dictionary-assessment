from flask import Flask, render_template
import sqlite3
from sqlite3 import Error, connect

app = Flask(__name__)
database = "databases.db"


def get_database():
    try:
        returned_db = sqlite3.connect(database)
        return returned_db
    except Error as error:
        print(error)


@app.route('/')
def render_home():
    con = get_database()

    return render_template('home.html')


if __name__ == '__main__':
    app.run()
