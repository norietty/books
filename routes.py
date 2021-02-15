import random
import requests
from application import app
from application import db
from application.models import User
from flask import Flask, session, render_template, url_for, request, flash, redirect, jsonify
from application.forms import RegistrationForm, LoginForm, SearchForm, ReviewSumbission
from flask_bcrypt import Bcrypt
from flask_login import login_required
#from helpers import login_required

bcrypt = Bcrypt(app)



@app.route("/home")
@login_required
def home():
    form = SearchForm()
    ids = tuple([random.randint(1, 5000)  for _ in range(10)])
    result = db.execute("SELECT * FROM books WHERE books.id IN :ids", {"ids": ids})
    return render_template("home.html", form=form, result=result)

@app.route("/search", methods=['GET', 'POST'])
@login_required
def search():
    """ Serach informations about a book"""
    ## get information form the form and query database then rander the page with the result 
    form = SearchForm()
    if form.validate_on_submit():
        search = form.search.data
        result = db.execute("SELECT * FROM books WHERE isbn  LIKE :search OR author LIKE :search OR title LIKE :search",
                        {"search": "%" + search + "%"}).fetchall()
        return render_template('search.html', result=result, form=form)
    return render_template('index.html', form=form)


@app.route("/book/<int:book_id>", methods=['GET','POST'])
@login_required
def book(book_id):
    """ This function going to add reviews submited by the user and desplaying information about each book"""
    form = ReviewSumbission()
    if form.validate_on_submit():
        db.execute("INSERT INTO reviews(review, stars, book_id, user_id) VALUES (:review, :stars, :book_id, :user_id)",
                    {"review": form.review.data, "stars": float(form.select.data), "book_id": book_id, "user_id": session['user_id']})
        db.commit()
        #return redirect(url_for('book'))
    # quering the data base for the book information and then rendring a page with all the info.
    book_info = db.execute("SELECT * FROM books WHERE books.id= :id",
                           {"id": book_id}).fetchall()[0]
    book_isbn = book_info['isbn']
    reviwes = db.execute("SELECT * FROM reviews WHERE reviews.book_id = :id", 
                          {"id": book_id}).fetchall()
    rating = db.execute("SELECT AVG(stars) as rating FROM reviews WHERE reviews.book_id = :id",
                         {"id": book_id}).fetchall()[0]['rating']
    review_user = db.execute("SELECT * FROM reviews WHERE reviews.book_id = :id and reviews.user_id = :user_id", 
                              {"id": book_id, "user_id": session['user_id']}).fetchall()
    ## get the goodreads infromations 
    res = requests.get("https://www.goodreads.com/book/review_counts.json",
                        params={"key": KEY, "isbns": book_isbn})
    data = res.json()
    data = data['books'][0]
    return render_template('book.html', book_info=book_info, rating=rating, review_user=review_user, reviwes=reviwes, form=form, data=data)


@app.route("/")
def index():
    return redirect(url_for('home'))


@app.route("/register", methods=['GET', 'POST'])
def register():
    """ This function for registering the user """
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        users = db.execute("SELECT * FROM users WHERE username= :username OR email= :email", 
                            {"username": form.username.data, "email": form.email.data}).fetchall()
        if users:
            flash('username  or email taken  please choose  another one', 'danger')
        else:
            db.execute('INSERT INTO users(username, email, password) values (:username, :email, :password)',
                         {"username": form.username.data, "email": form.email.data, "password": hashed_password})
            db.commit()
            flash(f'Account created  you can now log in', 'success')
            return redirect(url_for('login'))
    return render_template('register.html', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    """ This function for logging the user"""
    ## log in the user 

    form = LoginForm()
    if form.validate_on_submit():
        result = db.execute("SELECT * FROM users WHERE username= :username", 
                            {"username": form.username.data}).fetchall()
        # make sure that the user exist and the password match .
        if result and  bcrypt.check_password_hash(result[0]['password'], form.password.data):
            session['user_id'] = result[0]['id']
            flash(' You are now logged in', 'success')
            return redirect(url_for('home'))
        else:
            flash('Log in unsuccesful please try again:', 'danger')
    return render_template('login.html', form=form)


@app.route("/logout")
@login_required
def logout():
    """ Logging the user out """
    # loggin ou the user 
    session.clear()
    return redirect(url_for('login'))


@app.route("/api/<string:isbn>")
def api(isbn):
    """ constrcting the API"""
    # query the data base for the book informations 
    book = db.execute("SELECT * FROM BOOKS WHERE books.isbn= :isbn",
                       {"isbn": isbn}).fetchall()[0]
    # if no information found return an error 
    if len(book) == 0:
        return jsonify({"error": "Sorry no book with that isbn"}), 404
    else:
        # if the book is in the database return a josn object with the informations.
        book_id = book['id']
        reviews = db.execute("SELECT COUNT(id) as total_ratings, AVG(stars) as averge_ratings FROM reviews WHERE reviews.book_id= :id ", 
                            {"id": book_id}).fetchall()[0]
        return jsonify({
            "title": book['title'] ,
            "author":  book['author'],
            "year": book['year'],
            "isbn": book['isbn'] ,
            "review_count": reviews['total_ratings'],
            "average_rating": reviews['averge_ratings']
            })  
