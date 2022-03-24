import flask
from flask_restful import abort, Resource, reqparse
from data.sqlalchemy import db_session
from data.models.users import User
from data.models.lessons import Lesson

from datetime import datetime as dt


def abort_if_lessons_not_found(lessons_id):
    session = db_session.create_session()
    lessons = session.query(Lesson).get(lessons_id)
    if not lessons:
        abort(404, message=f"Lesson {lessons_id} not found")


def get_access_level(token: str) -> str:
    session = db_session.create_session()
    user = session.query(User).filter(User.token == token).first()
    if user:
        return user.access_level
    else:
        abort(403, message=f"Unknown api-key")


parser_oneEl = reqparse.RequestParser()
parser_oneEl.add_argument('api-key', required=True, type=str)


class LessonsResource(Resource):
    def get(self, lessons_id):
        args = parser_oneEl.parse_args()
        abort_if_lessons_not_found(lessons_id)
        session = db_session.create_session()
        lessons = session.query(Lesson).get(lessons_id)
        level = get_access_level(args['api-key'])
        if level == 3:
            return flask.jsonify({'lessons': lessons.to_dict(rules=('-user',))})
        elif level == 2:
            if args['api-key'] == lessons.user.token:
                return flask.jsonify({'lessons': lessons.to_dict(rules=('-user',))})
            else:
                abort(403, message=f"Access denied")
        elif level == 1:
            users = session.query(User).filter(User.grade == lessons.grade)
            if args['api-key'] in [el.token for el in users]:
                return flask.jsonify({'lessons': lessons.to_dict(rules=('-user',))})
            else:
                abort(403, message=f"Access denied")

    def delete(self, lessons_id):
        args = parser_oneEl.parse_args()
        abort_if_lessons_not_found(lessons_id)
        level = get_access_level(args['api-key'])
        if level == 3:
            session = db_session.create_session()
            lessons = session.query(Lesson).get(lessons_id)
            session.delete(lessons)
            session.commit()
            return flask.jsonify({'success': 'OK'})
        else:
            abort(403, message=f"Access denied")


parser = reqparse.RequestParser()
parser.add_argument('api-key', required=True, type=str)
parser.add_argument('id', required=False, type=int)
parser.add_argument('topic', required=True, type=str)
parser.add_argument('grade', required=True, type=str)
parser.add_argument('teacher', required=False, type=int)
parser.add_argument('cabinet', required=True, type=str)
parser.add_argument('start_date', required=True, type=str)
parser.add_argument('end_date', required=True, type=str)


class LessonsListResource(Resource):
    def get(self):
        args = parser_oneEl.parse_args()
        level = get_access_level(args['api-key'])
        if level == 3:
            session = db_session.create_session()
            lessons = session.query(Lesson).all()
            return flask.jsonify({'lessons': [item.to_dict(rules=('-user',))
                                              for item in lessons]})
        else:
            abort(403, message=f"Access denied")

    def post(self):
        args = parser.parse_args()
        level = get_access_level(args['api-key'])
        if level == 3:
            session = db_session.create_session()
            lessons = Lesson(
                id=args['id'],
                topic=args['topic'],
                grade=args['grade'],
                teacher=args['teacher'],
                cabinet=args['cabinet'],
                start_date=dt.strptime(args['start_date'], '%Y-%m-%d %H:%M:%S'),
                end_date=dt.strptime(args['end_date'], '%Y-%m-%d %H:%M:%S'),
            )
            session.add(lessons)
            session.commit()
            return flask.jsonify({'success': 'OK'})
        else:
            abort(403, message=f"Access denied")
