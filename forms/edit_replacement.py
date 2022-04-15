from wtforms import SubmitField, StringField
from wtforms.fields import DateTimeField
from wtforms.validators import DataRequired
from flask_wtf import FlaskForm


class EditReplacementForm(FlaskForm):
    teacher = StringField('Учитель', validators=[DataRequired()])
    time = StringField('Время', validators=[DataRequired()])
    grade = StringField('Класс', validators=[DataRequired()])
    topic = StringField('Название урока', validators=[DataRequired()])
    cabinet = StringField('Кабинет', validators=[DataRequired()])
    submit = SubmitField('Сохранить измениния   ')
