from wtforms import PasswordField, SubmitField, EmailField, StringField, SelectField
from wtforms.validators import DataRequired
from flask_wtf import FlaskForm


class EditUsersForm(FlaskForm):
    id = StringField('id')
    token = StringField('Токен')
    grade = StringField('Класс')
    access_level = SelectField('Уровень доступа', choices=[(3, 3), (2, 2), (1, 1)])
    surname = StringField('Фамилия')
    name = StringField('Имя')
    patronymic = StringField('Отчество')
    email = EmailField('Почта')
    password = PasswordField('Пароль')
    submit = SubmitField('Сохранить')
