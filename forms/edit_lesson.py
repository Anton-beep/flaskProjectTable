from flask_wtf import FlaskForm
from sqlalchemy import or_
from wtforms import SubmitField, StringField, SelectField
from wtforms.validators import DataRequired

from data.models.users import User
from data.sqlalchemy import db_session


class EditLessonForm(FlaskForm):
    title = StringField('', validators=[DataRequired()])
    rep_teacher = StringField('', validators=[DataRequired()])
    time = StringField('Время', validators=[DataRequired()])
    grade = StringField('Класс', validators=[DataRequired()])
    topic = StringField('Название урока', validators=[DataRequired()])
    cabinet = StringField('Кабинет', validators=[DataRequired()])

    db_session.global_init("db/timetable.db")
    db_sess = db_session.create_session()
    teachers = [element.surname + ' ' + element.name for element in
                db_sess.query(User).filter(or_(User.access_level == 3, User.access_level == 2))]
    teachers = [(element, element) for element in teachers]

    teacher = SelectField('Учитель', choices=teachers, validators=[DataRequired()])
    submit = SubmitField('Сохранить измениния')

