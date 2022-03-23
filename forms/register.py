from wtforms import PasswordField, SubmitField, EmailField, StringField, SelectField
from wtforms.validators import DataRequired
from flask_wtf import FlaskForm


class RegisterForm(FlaskForm):
    token = StringField('Токен', validators=[DataRequired()])
    grade = StringField('Класс')
    access_level = SelectField('Уровень доступа', choices=[(1, 1), (2, 2), (3, 3)])
    surname = StringField('Фамилия')
    name = StringField('Имя')
    patronymic = StringField('Отчество')
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_again = PasswordField('Повторите пароль', validators=[DataRequired()])
    submit = SubmitField('Зарегестрироваться')
