from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager
from application import db1, login_manager


# Creating the classes for creating tables in the database.
class Reviews(db1.Model):
    __tablename__ = "reviews"
    id = db1.Column(db1.Integer, primary_key=True)
    review = db1.Column(db1.String, nullable=False)
    stars = db1.Column(db1.Float, nullable=False)
    book_id = db1.Column(db1.Integer, db1.ForeignKey('books.id'))
    user_id = db1.Column(db1.Integer, db1.ForeignKey('users.id'))


class Books(db1.Model):
    __tablename__ = "books"
    id = db1.Column(db1.Integer, primary_key=True)
    isbn = db1.Column(db1.String, nullable=False)
    title = db1.Column(db1.String(50), nullable=False)
    author = db1.Column(db1.String(50), nullable=False)
    year = db1.Column(db1.String, nullable=False)
    reviews = db1.relationship('Reviews', backref='book', lazy=True)


class User(UserMixin, db1.Model):
    __tablename__ = "users"
    id = db1.Column(db1.Integer, primary_key=True)
    username = db1.Column(db1.String(20), unique=True, nullable=False)
    email = db1.Column(db1.String(50), unique=True, nullable=False)
    password = db1.Column(db1.String(60), nullable=False)
    reviews = db1.relationship('Reviews', backref='author', lazy=True)



@login_manager.user_loader
def load_user(user_id):
    return None