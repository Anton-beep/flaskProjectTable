from wtforms import PasswordField, SubmitField, EmailField, BooleanField, StringField
from wtforms.validators import DataRequired
from flask_wtf import FlaskForm


class LoginForm(FlaskForm):
    token = StringField('Токен')
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')
