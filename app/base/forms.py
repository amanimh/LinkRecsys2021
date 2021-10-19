# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from flask_wtf import FlaskForm
from flask_login import current_user
from wtforms import TextField, PasswordField,SelectField,StringField,SubmitField,BooleanField,TextAreaField,Field
from wtforms.validators import InputRequired, Email, DataRequired,Length,ValidationError,EqualTo

from app.base.models import User,Job

## login and registration

class LoginForm(FlaskForm):
    username = TextField    ('Username', id='username_login' )
    password = PasswordField('Password', id='pwd_login')

class CreateAccountForm(FlaskForm):
    username = TextField('Username'     , id='username_create' , validators=[DataRequired('nom utilisateur obligatoire'),Length(min=5,max=10,message='must be between 5or 10')])
    email    = TextField('Email'        , id='email_create'    , validators=[DataRequired(), Email()])
    password = PasswordField('Password' , id='pwd_create'      , validators=[DataRequired()])
    poste = SelectField('poste',id='poste_create',choices=[('admin','Administrateur') , ('Talaq','Talent acquisition')])
    pic =TextField('image',id='image_create', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')
    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('Ce nom d utilisateur est déjà pris. Veuillez en choisir un autre.')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('Cet e-mail est pris. Veuillez en choisir un autre.')


class UpdateAccountForm(FlaskForm):
    username = TextField('Username'     , id='username_create' , validators=[InputRequired('nom utilisateur obligatoire'),Length(min=5,max=10,message='must be between 5or 10')])
    email    = TextField('Email'        , id='email_create'    , validators=[DataRequired(), Email()])
    current_password = PasswordField('Password', id='current_password', validators=[DataRequired()])
    new_password = PasswordField('Password', id='new_password', validators=[DataRequired()])
    confirm_password = PasswordField('Password', id='confirm_password', validators=[DataRequired()])
    submit = SubmitField('Modifier')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('Ce nom d utilisateur est déjà pris. Veuillez en choisir un autre.')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('Cet e-mail est pris. Veuillez en choisir un autre.')




class RequestResetForm(FlaskForm):
    email = StringField('Email',validators=[DataRequired(), Email()])
    submit = SubmitField(' Réinitialiser ')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('Il n y a pas de compte avec cet e-mail. Vous devez d abord vous inscrire..')



class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')


