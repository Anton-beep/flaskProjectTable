from wtforms import PasswordField, SubmitField, EmailField, StringField, SelectField
from wtforms.validators import DataRequired
from flask_wtf import FlaskForm


class RegisterAdminForm(FlaskForm):
    grade = StringField('Класс')
    access_level = SelectField('Уровень доступа', choices=[(3, 3), (2, 2), (1, 1)],
                               validators=[DataRequired()], default=1)
    surname = StringField('Фамилия')
    name = StringField('Имя')
    patronymic = StringField('Отчество')
    submit = SubmitField('Зарегестрировать пользователя')
