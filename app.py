from flask import Flask, render_template, request, redirect, session
import sqlite3
from sqlite3 import Error, connect
from datetime import datetime, timezone
from flask_bcrypt import Bcrypt

app = Flask(__name__)
database = "C:/Users/20249/OneDrive - Wellington College/13dts/assesmetn/dbs"#"C:/Users/Felix/PycharmProjects/dictionary-assessment/dbs"
app.secret_key = "bling bloing i love keyyyyyyyyyyysssssssssssssssssssssssss :)))))))))))))))))))))))))))))))))))))) ok "


def get_database(database_file):
    try:
        returned_db = sqlite3.connect(database_file)
        return returned_db
    except Error as error:
        print(error)


@app.route("/")
def render_base():
    return render_template('base.html')


@app.route('/signup', methods=['POST', 'GET'])
def render_signup():
    if request.method == 'POST':
        firstname = request.form.get('firstname').strip().title()
        lastname = request.form.get('lastname').strip().title()
        email = request.form.get('email').strip().lower()
        password = request.form.get('password').strip()
        password2 = request.form.get('password2').strip()
        usertype_box = request.form.get('usertype')

        if usertype_box == 'on':
            usertype = 'teacher'
        else:
            usertype = 'student'

        if password != password2:
            return redirect('/signup?error=passwords+must+match')

        if len(password) < 8:
            return redirect('/signup?error=password+must+be+at+least+8+characters')
        con = get_database(database)
        query = "INSERT INTO users (firstname, lastname, email, password, usertype) VALUES (?, ?, ?, ?, ?)"
        cur = con.cursor()

        try:
            cur.execute(query, (firstname, lastname, email, password, usertype))
        except sqlite3.IntegrityError:
            con.close()
            return redirect('/signup?error=email+already+in+use')
        con.commit()
        con.close()

        return redirect('/login')

    return render_template('signup.html')


@app.route('/login', methods=['POST', 'GET'])
def render_login():
    if request.method == 'POST':
        email = request.form.get('email').strip().lower()
        password = request.form.get('password').strip()
        query = "SELECT primarykey, firstname, email, password, usertype FROM users WHERE email = ?"
        con = get_database(database)
        cur = con.cursor()
        cur.execute(query, (email,))
        user_info = cur.fetchone()
        con.close()
        try:
            user_key = user_info[0]
            username = user_info[1]
            user_email = user_info[2]
            user_password = user_info[3]
            usertype = user_info[4]
        except IndexError:
            return redirect('/login?error=email+or+password+incorrect')
        if password != user_password:
            return redirect('/login?error=email+or+password+incorrect')
        session['user_key'] = user_key
        session['username'] = username
        session['user_email'] = user_email
        session['usertype'] = usertype
        print(session)
        return redirect('/home')
    return render_template('login.html')


@app.route('/home')
def render_home():
    return render_template('home.html')


@app.route('/all_words')
def render_all_words():
    con = get_database(database)
    query = "SELECT primarykey, englishword, tereoword FROM words"
    cur = con.cursor()
    cur.execute(query)
    info = cur.fetchall()
    return render_template('all_words.html', words_table=info)


@app.route('/all_words/<word>')
def render_specific_word(word):
    con = get_database(database)
    query = "SELECT englishword, tereoword, category, definition, level, submitdate FROM words WHERE englishword=?"
    cur = con.cursor()
    cur.execute(query, (word,))
    info = cur.fetchall()
    print(info)
    return render_template('specific_word.html', word_info=info, passing_word=word)


@app.route('/category_list')
def render_category_list():
    con = get_database(database)
    query = "SELECT category FROM words"
    cur = con.cursor()
    cur.execute(query)
    info = cur.fetchall()
    return render_template("category_list.html", category=info)


@app.route('/category_list/<category>')
def render_specific_category(category):
    con = get_database(database)
    query = "SELECT englishword, tereoword FROM words WHERE category=?"
    cur = con.cursor()
    cur.execute(query, (category,))
    info = cur.fetchall()
    return render_template("specific_category.html", category=info, passing_category=category)


@app.route('/all_words/<word>/delete', methods=['POST', 'GET'])
def render_delete(word):
    print(word)
    if 'usertype' in session:
        if session['usertype'] == 'student':
            return redirect(request.referrer + '?error=no+permission')
        else:
            if request.method == 'POST':
                con = get_database(database)
                query = "DELETE FROM words WHERE englishword=?"
                cur = con.cursor()
                print(1)
                try:
                    cur.execute(query, (word,))
                    var = cur.fetchall()
                    con.commit()
                    con.close()
                    return redirect('/home?deleted')
                except sqlite3.IntegrityError:
                    return redirect('/?failed')
            else:
                return render_template('delete.html')
    else:
        return redirect('/signup?no+session+detected')


@app.route('/all_words/add', methods=['POST', 'GET'])
def render_add():
    if 'usertype' in session:
        if session['usertype'] == 'student':
            return redirect(request.referrer + '?error=no+permission')
        else:
            if request.method == 'POST':
                englishword = request.form.get('englishword').lower().strip()
                tereoword = request.form.get('tereoword').lower().strip()
                category = request.form.get('category').lower().strip()
                definition = request.form.get('definition')
                level = request.form.get('level')
                submitdate = datetime.now(timezone.utc)
                con = get_database(database)
                query = "INSERT INTO words ('englishword', 'tereoword', 'category', 'definition', 'level', submitdate)  VALUES (?, ?, ?, ?, ?, ?)"
                cur = con.cursor()
                cur.execute(query, (englishword, tereoword, category, definition, level, submitdate))
                con.commit()
                con.close()
                return redirect('/home?added')
            else:
                return render_template('add.html')
    else:
        return redirect('/signup?no+session+detected')


@app.route('/logout')
def logout():
    session.pop('user_key', None)
    session.pop('username', None)
    session.pop('user_email', None)
    session.pop('usertype', None)
    print(session)
    return redirect('/?logged+out')


if __name__ == '__main__':
    app.run()
