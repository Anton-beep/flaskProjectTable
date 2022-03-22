from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from flask_wtf import FlaskForm


class TokenForm(FlaskForm):
    token = StringField('Токен', validators=[DataRequired()])
    submit = SubmitField('Продолжить')
