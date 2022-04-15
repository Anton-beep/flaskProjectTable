from wtforms import PasswordField, SubmitField, EmailField, BooleanField, StringField
from wtforms.validators import DataRequired
from flask_wtf import FlaskForm


class EditLessonForm(FlaskForm):
    title = StringField('', validators=[DataRequired()])
    teacher = StringField('Учитель', validators=[DataRequired()])
    time = StringField('Время', validators=[DataRequired()])
    grade = StringField('Класс', validators=[DataRequired()])
    topic = StringField('Название урока', validators=[DataRequired()])
    cabinet = StringField('Кабинет', validators=[DataRequired()])
    submit = SubmitField('Сохранить измениния')
