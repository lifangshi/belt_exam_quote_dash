from flask import Flask, render_template, request, redirect, session, flash
import re
import mysqlconnection
from flask_bcrypt import Bcrypt
import datetime
app = Flask(__name__)
app.secret_key="keep it secret, keep it safe"
bcrypt = Bcrypt(app)

@app.route('/')
def login_registration():
    return render_template("login.html")

@app.route('/registration', methods=["POST"])
def registration():
    email_regex = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
    name_regex= re.compile(r'^[a-zA-z][a-zA-z]+$')
    password_validation = re.compile(r'^(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{8,}$')

    if (len(request.form['first_name']) < 2) or (None == (name_regex.match(request.form['first_name']))):
        flash("Please enter a first name") 
    if (len(request.form['last_name']) < 2) or (None == (name_regex.match(request.form['last_name']))):
        flash("Please enter a last name")
    if (len(request.form['email']) < 6) or (None == (email_regex.match(request.form['email']))):
        flash("Please enter a valid email")
    if (len(request.form['password']) < 8) and (not (password_validation.match(request.form['password']))):
        flash("Password should be at least 8 characters and have at least 1 number and 1 uppercase letter") 
    if request.form['confirm_password'] != request.form['password']:
        flash("Comformation_password should matches password")

    if not '_flashes' in session.keys():
        mysql = mysqlconnection.MySQLConnection("belt_exam")
        query = "INSERT INTO users (first_name, last_name, email, password) VALUE(%(fn)s, %(ls)s, %(em)s, %(ps)s);"
        data={
            "fn": request.form['first_name'],
            "ls": request.form['last_name'],
            "em": request.form['email'],
            "ps": bcrypt.generate_password_hash(request.form['password']),
        }
        user_id = mysql.query_db(query, data)
        
        session['user_id'] = user_id
        print('userID',user_id)
        if user_id:
            print('goto login success')
            session['first_name'] = request.form['first_name']
            return redirect('/quotes')
        else:
            flash("Something went wrong, prabably email already registered.")
            return redirect('/')
    else:
        return redirect('/') 


@app.route('/login', methods=["POST"])
def login():
    mysql = mysqlconnection.MySQLConnection("belt_exam")
    query = "SELECT id, first_name, password FROM users WHERE email = %(email)s;"
    data = { 'email': request.form['email']}
    
    result = mysql.query_db(query, data)
    if(len(result) == 0):
        flash('Email or password is invalid')
        return redirect ('/')
    if(bcrypt.check_password_hash(result[0]['password'], request.form['password'])):
        session['first_name'] = result[0]['first_name']
        session['user_id'] = result[0]['id']

        print('try to go to dashboard')
        return redirect('/quotes') 
    else:
        flash('Email or password is invalid')
        return redirect('/')


@app.route("/quotes/create", methods=["POST"])
def add_quote_to_db():
    print(request.form)
    if (len(request.form['author']) <= 3):
        flash("The author must consist more than 3 characters") 
    if (len(request.form['quote']) <=10):
        flash("The quote must consist more than 10 characters!")

    if not '_flashes' in session.keys():
        mysql = mysqlconnection.MySQLConnection("belt_exam")
        query = "INSERT INTO quotes (author, quote, user_id) VALUE (%(author)s, %(quote)s, %(user_id)s);"
        data = {
            "author": request.form['author'],
            "quote": request.form["quote"],
            "user_id": session["user_id"]
        }
        quote_id = mysql.query_db(query, data)
        print('*****'*10, quote_id)
        print(1)
    return redirect("/quotes")


@app.route('/quotes')
def seccess():
    print(session.keys())
    if 'user_id' in session.keys():
        print(2)
        data = { 'user_id': session['user_id']}
        print(data)
        mysql = mysqlconnection.MySQLConnection("belt_exam")
        query = "SELECT * FROM quotes;"
        quotes = mysql.query_db(query, data)

        mysql = mysqlconnection.MySQLConnection("belt_exam")
        query = "SELECT * FROM users WHERE id = %(user_id)s;"
        user = mysql.query_db(query, data)
        print(user)
        print("#"*50, quotes)
        for quote in quotes:
            mysql = mysqlconnection.MySQLConnection("belt_exam")
            query = "SELECT * FROM users_has_quotes WHERE quote_id = %(quote_id)s;"
            data = { 'quote_id': quote['id']}
            quote_data = mysql.query_db(query, data)
            quote['like_count'] = len(quote_data)
            
            mysql = mysqlconnection.MySQLConnection("belt_exam")
            query = "SELECT * FROM users WHERE id = %(user_id)s;"
            data = { 'user_id': quote['user_id']}
            user_data = mysql.query_db(query, data)
            quote['user_name'] = user_data[0]['first_name']+' '+user_data[0]['last_name']
        return render_template('dash.html', all_quotes = quotes, user = user[0])
    else:
        return redirect('/')

@app.route('/like/<quote_id>')
def like_quote(quote_id):
    data={
        "user_id": session['user_id'],
        "quote_id": quote_id,
    }
    #check if the user has already liked the quote
    mysql = mysqlconnection.MySQLConnection("belt_exam")
    query = "SELECT * FROM users_has_quotes WHERE user_id = %(user_id)s AND quote_id = %(quote_id)s;"
    like_quote_status = mysql.query_db(query, data)
    if(len(like_quote_status)>0):
        flash('you have already liked this quote')
    else:
        mysql = mysqlconnection.MySQLConnection("belt_exam")
        query = "INSERT INTO users_has_quotes (user_id, quote_id) VALUE(%(user_id)s, %(quote_id)s);"
        user_id = mysql.query_db(query, data)
    return redirect('/quotes')

@app.route('/delete/<quote_id>')
def delete_quote(quote_id):
    data={
        "quote_id": quote_id,
    }
    #check if the user has already liked the quote
    mysql = mysqlconnection.MySQLConnection("belt_exam")
    query = "DELETE FROM users_has_quotes WHERE quote_id = %(quote_id)s;"
    mysql.query_db(query, data)

    mysql = mysqlconnection.MySQLConnection("belt_exam")
    query = "DELETE FROM quotes WHERE id = %(quote_id)s;"
    mysql.query_db(query, data)
    return redirect('/quotes')

@app.route('/user/<user_id>')
def view_user(user_id):
    data={
        "user_id": user_id,
    }
    mysql = mysqlconnection.MySQLConnection("belt_exam")
    query = "SELECT * FROM quotes WHERE user_id = %(user_id)s;"
    quotes = mysql.query_db(query, data)
    mysql = mysqlconnection.MySQLConnection("belt_exam")
    query = "SELECT * FROM users WHERE id = %(user_id)s;"
    user = mysql.query_db(query, data)[0]
    print(user)
    return render_template('view_user.html', quotes = quotes, user = user)

@app.route('/edit')
def edit_user():
    data={
        "user_id": session['user_id'],
    }
    mysql = mysqlconnection.MySQLConnection("belt_exam")
    query = "SELECT * FROM users WHERE id = %(user_id)s;"
    user = mysql.query_db(query, data)[0]
    print(user)
    return render_template('edit.html', user = user)

@app.route('/update', methods = ['POST'])
def update_user():
    # mysql = mysqlconnection.MySQLConnection("belt_exam")
    # query = "SELECT * FROM users WHERE id = %(user_id)s;"
    # user = mysql.query_db(query, data)[0]

    email_regex = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
    name_regex= re.compile(r'^[a-zA-z][a-zA-z]+$')

    if (len(request.form['first_name']) < 2) or (None == (name_regex.match(request.form['first_name']))):
        flash("Please enter a first name") 
    if (len(request.form['last_name']) < 2) or (None == (name_regex.match(request.form['last_name']))):
        flash("Please enter a last name")
    if (len(request.form['email']) < 6) or (None == (email_regex.match(request.form['email']))):
        flash("Please enter a valid email")

    if not '_flashes' in session.keys():
        mysql = mysqlconnection.MySQLConnection("belt_exam")
        query = 'UPDATE users SET first_name = %(first_name)s, last_name=%(last_name)s, email=%(email)s WHERE id = %(id)s;'
        data = {
            "first_name": request.form["first_name"], 
            "last_name": request.form["last_name"],
            "email": request.form["email"],
            "id": session["user_id"],
        }
        response = mysql.query_db(query, data)
        print('ADASDASDASDASD',response)
        if(None == response):
            return redirect('/quotes')
        elif(not response):
            flash('email already taken')
            return redirect('/edit')
    return redirect("/edit")


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')


if __name__ == "__main__":
    app.run(debug=True)