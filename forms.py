from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, BooleanField
from wtforms.validators import (
    DataRequired,
    Email,
    EqualTo,
    Length,
    Optional,
)


class SignupForm(FlaskForm):
    username = StringField(
        "Username", validators=[DataRequired(), Length(min=3, max=80)]
    )
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField(
        "Password", validators=[DataRequired(), Length(min=8, max=128)]
    )
    confirm_password = PasswordField(
        "Confirm Password",
        validators=[DataRequired(), EqualTo("password", message="Passwords must match")],
    )


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember = BooleanField("Remember me")


class PromptBuilderForm(FlaskForm):
    expertise = StringField(
        "Give one field of expertise your AI should be a master of",
        validators=[DataRequired(), Length(max=200)],
    )
    task = TextAreaField(
        "Describe the main task you want your AI to perform",
        validators=[DataRequired(), Length(max=2000)],
    )
    context = TextAreaField(
        "Give as much context as possible",
        validators=[DataRequired(), Length(max=5000)],
    )
    constraints = TextAreaField(
        "Name any constraints, if applicable",
        validators=[Optional(), Length(max=2000)],
    )
