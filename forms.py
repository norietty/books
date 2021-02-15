from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField, TextAreaField
from wtforms.validators import Required, Length, Email, EqualTo


class RegistrationForm(FlaskForm):
    username = StringField("Username", validators=[Required(),
                           Length(min=2, max=20)])
    email = StringField("Email", validators=[Required(), Email()])
    password = PasswordField("Password", validators=[Required()])
    confirm_password = PasswordField("Confirm password",
                                     validators=[Required(),
                                                 EqualTo("password")])
    submit = SubmitField('Sign up')


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[Required(),
                           Length(min=2, max=20)])
    password = PasswordField("Password", validators=[Required()])
    remember = BooleanField("Remember me")
    submit = SubmitField("Log in")


class SearchForm(FlaskForm):
    select = SelectField(choices=[('isbn', 'isbn'), ('title', 'title'), ('author', 'author')])
    search = StringField("Search a book ")
    submit = SubmitField("search")

class ReviewSumbission(FlaskForm):
    select = SelectField(choices=[('1', '1'), ('1.5', '1.5'), ('2', '2'), ('2.5', '2.5'), ('3', '3'), ('3.5', '3.5'), ('4', '4'), ('4,5', '4.5'), ('5', '5')])
    review = TextAreaField()
    submit = SubmitField("Submit")