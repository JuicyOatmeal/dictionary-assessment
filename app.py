from flask import Flask, render_template, request, redirect, session
import sqlite3
from sqlite3 import Error, connect
from datetime import datetime, timezone
from flask_bcrypt import Bcrypt

app = Flask(__name__)
database = "C:/Users/20249/OneDrive - Wellington College/13dts/assesmetn/dbs"
app.secret_key = "bling bloing i love keyyyyyyyyyyysssssssssssssssssssssssss :)))))))))))))))))))))))))))))))))))))) ok"
# a secret key that needs to be hard to guess


def get_database(database_file):  # finds the database so that the program can use it to store and retrieve data.
    try:
        returned_db = sqlite3.connect(database_file)
        return returned_db
    except Error as error:  # protection in case of errors.
        print(error)


@app.route("/")  # renders the base page, where the user can log in, make an account, or continue to the home page.
def render_base():
    return render_template('base.html')


@app.route('/signup', methods=['POST', 'GET'])  # renders the signup page
def render_signup():
    if request.method == 'POST':  # a form for the user to input their information in order to make an account
        firstname = request.form.get('firstname').strip().title()
        lastname = request.form.get('lastname').strip().title()
        email = request.form.get('email').strip().lower()
        password = request.form.get('password').strip()
        password2 = request.form.get('password2').strip()
        usertype_box = request.form.get('usertype')

        if usertype_box == 'on':  # assigns the account the 'teacher' usertype if the 'Teacher?' box is checked
            usertype = 'teacher'
        else:
            usertype = 'student'

        if password != password2:  # gives an error if the passwords don't match
            return redirect('/signup?error=passwords+must+match')

        if len(password) < 8:  # gives an error if the password isn't at least 8 characters
            return redirect('/signup?error=password+must+be+at+least+8+characters')
        con = get_database(database)
        query = "INSERT INTO users (firstname, lastname, email, password, usertype) VALUES (?, ?, ?, ?, ?)"
        cur = con.cursor()

        try:  # sends the form's information to the database
            cur.execute(query, (firstname, lastname, email, password, usertype))
        except sqlite3.IntegrityError:  # checks the email provided doesn't already have an account associated
            con.close()
            return redirect('/signup?error=email+already+in+use')
        con.commit()
        con.close()

        return redirect('/login')

    return render_template('signup.html')


@app.route('/login', methods=['POST', 'GET'])  # renders the login page
def render_login():
    if request.method == 'POST':  # a form containing email and password boxes
        email = request.form.get('email').strip().lower()
        password = request.form.get('password').strip()
        query = "SELECT primarykey, firstname, email, password, " \
                "usertype FROM users WHERE email = ?"  # stores information of user, based on their email
        con = get_database(database)
        cur = con.cursor()
        cur.execute(query, (email,))
        user_info = cur.fetchone()
        con.close()
        try:  # assigns the user a cookie, so they can be recognised by other web pages on the site
            user_key = user_info[0]
            username = user_info[1]
            user_email = user_info[2]
            user_password = user_info[3]
            usertype = user_info[4]
        except IndexError:  # catches any errors
            return redirect('/login?error=email+or+password+incorrect')
        if password != user_password:  # if the password isn't the same, reset the page with an error message
            return redirect('/login?error=email+or+password+incorrect')
        session['user_key'] = user_key
        session['username'] = username
        session['user_email'] = user_email
        session['usertype'] = usertype
        print(session)
        return redirect('/home')
    return render_template('login.html')


@app.route('/home')  # renders the home page
def render_home():
    return render_template('home.html')


@app.route('/all_words')  # renders the all words page, which includes all words in the database
def render_all_words():
    con = get_database(database)
    query = "SELECT primarykey, englishword, " \
    "tereoword FROM words"  # stores the primary key, english word and te reo word of each word in the database
    cur = con.cursor()
    cur.execute(query)
    info = cur.fetchall()
    return render_template('all_words.html', words_table=info)


@app.route('/all_words/<word>')  # renders the page of a specified word. When the word is clicked,
def render_specific_word(word):  # that word is passed through the 'render_specific_word' method, by way of 'word'
    con = get_database(database)
    query = "SELECT englishword, tereoword, category, definition, " \
    "level, submitdate FROM words WHERE englishword=?"  # stores certain info from the english word matching 'word'
    cur = con.cursor()
    cur.execute(query, (word,))
    info = cur.fetchall()
    print(info)
    return render_template('specific_word.html', word_info=info, passing_word=word)  # renders the html page,
    # passing the word to that page using the 'passing_word' variable.


@app.route('/category_list')  # renders the list of categories,
def render_category_list():  # which users can click on to only show words from that category
    con = get_database(database)
    query = "SELECT category FROM words"  # stores all categories from the database
    cur = con.cursor()
    cur.execute(query)
    info = cur.fetchall()
    return render_template("category_list.html", category=info)


@app.route('/category_list/<category>')  # renders a list of all words in the selected category, which
def render_specific_category(category):  # is passed using the 'render_specific_category' method by way of 'category'
    con = get_database(database)
    query = "SELECT englishword, tereoword FROM words WHERE category=?"  # stores info from the selected category
    cur = con.cursor()
    cur.execute(query, (category,))
    info = cur.fetchall()
    return render_template("specific_category.html", category=info, passing_category=category)


@app.route('/all_words/<word>/delete', methods=['POST', 'GET'])  # renders the page which allows words to be removed
def render_delete(word):  # passes the word to be deleted through the 'render_delete' method, using variable 'word'
    if 'usertype' in session:  # makes sure the user is logged in
        if session['usertype'] == 'student':  # doesn't allow students to delete words
            return redirect(request.referrer + '?error=no+permission')
        else:
            if request.method == 'POST':
                con = get_database(database)
                query = "DELETE FROM words WHERE englishword=?"
                cur = con.cursor()
                try:
                    cur.execute(query, (word,))  # tries to delete word in database that matches the 'word' variable
                    var = cur.fetchall()
                    con.commit()
                    con.close()
                    return redirect('/home?deleted')  # return the user home with message 'deleted'
                except sqlite3.IntegrityError:  # catches any error that occurs with deleting
                    return redirect('/?failed')
            else:
                return render_template('delete.html')
    else:
        return redirect('/signup?no+session+detected')


@app.route('/all_words/add', methods=['POST', 'GET'])  # renders the page where words can be added
def render_add():
    if 'usertype' in session:  # checks the user is logged in
        if session['usertype'] == 'student':  # doesn't allow student accounts to add words
            return redirect(request.referrer + '?error=no+permission')
        else:  # a form that requests the information required to add a new word to the database
            if request.method == 'POST':
                englishword = request.form.get('englishword').lower().strip()
                tereoword = request.form.get('tereoword').lower().strip()
                category = request.form.get('category').lower().strip()
                definition = request.form.get('definition')
                level = request.form.get('level')
                submitdate = datetime.now(timezone.utc)
                con = get_database(database)
                query = "INSERT INTO words ('englishword', 'tereoword', 'category', 'definition', 'level', " \
                        "submitdate)  VALUES (?, ?, ?, ?, ?, ?)"  # inputs the new word into the database
                cur = con.cursor()
                cur.execute(query, (englishword, tereoword, category, definition, level, submitdate))
                con.commit()
                con.close()
                return redirect('/home?added')  # return the user home with message 'added'
            else:
                return render_template('add.html')
    else:
        return redirect('/signup?no+session+detected')


@app.route('/logout')  # sets the user's cookie to none, and redirects them with the message 'logged out'
def logout():
    session.pop('user_key', None)
    session.pop('username', None)
    session.pop('user_email', None)
    session.pop('usertype', None)
    print(session)
    return redirect('/?logged+out')


if __name__ == '__main__':  # runs this script
    app.run()
