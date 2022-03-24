import sqlalchemy
from sqlalchemy import orm
from ..sqlalchemy.db_session import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin


class Replacement(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'replacements'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    lesson = sqlalchemy.Column(sqlalchemy.Integer,
                                  sqlalchemy.ForeignKey("lessons.id"))
    lessons = orm.relation('Lesson')
    topic = sqlalchemy.Column(sqlalchemy.String)
    grade = sqlalchemy.Column(sqlalchemy.String)
    teacher = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("users.id"))
    user = orm.relation('User')
    cabinet = sqlalchemy.Column(sqlalchemy.String)
    start_date = sqlalchemy.Column(sqlalchemy.DateTime)
    end_date = sqlalchemy.Column(sqlalchemy.DateTime)
