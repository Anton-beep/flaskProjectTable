import flask
from flask_restful import abort, Resource, reqparse
from data.sqlalchemy import db_session
from data.models.users import User
from data.models.replacements import Replacement

from datetime import datetime as dt


def abort_if_replacement_not_found(replacements_id):
    session = db_session.create_session()
    lessons = session.query(Replacement).get(replacements_id)
    if not lessons:
        abort(404, message=f"Replacement {replacements_id} not found")


def get_access_level(token: str) -> str:
    session = db_session.create_session()
    user = session.query(User).filter(User.token == token).first()
    if user:
        return user.access_level
    else:
        abort(403, message=f"Unknown api-key")


parser_oneEl = reqparse.RequestParser()
parser_oneEl.add_argument('api-key', required=True, type=str)


class ReplacementsResource(Resource):
    def get(self, replacements_id):
        args = parser_oneEl.parse_args()
        abort_if_replacement_not_found(replacements_id)
        session = db_session.create_session()
        replacements = session.query(Replacement).get(replacements_id)
        level = get_access_level(args['api-key'])
        if level == 3:
            return flask.jsonify(
                {'replacements': replacements.to_dict(rules=('-user', '-lessons'))})
        elif level == 2:
            if args['api-key'] == replacements.user.token:
                return flask.jsonify(
                    {'lessons': replacements.to_dict(rules=('-user', '-lessons'))})
            else:
                abort(403, message=f"Access denied")
        elif level == 1:
            users = session.query(User).filter(User.grade == replacements.grade)
            if args['api-key'] in [el.token for el in users]:
                return flask.jsonify(
                    {'replacements': replacements.to_dict(rules=('-user', '-lessons'))})
            else:
                abort(403, message=f"Access denied")

    def delete(self, replacements_id):
        args = parser_oneEl.parse_args()
        abort_if_replacement_not_found(replacements_id)
        level = get_access_level(args['api-key'])
        if level == 3:
            session = db_session.create_session()
            replacements = session.query(Replacement).get(replacements_id)
            session.delete(replacements)
            session.commit()
            return flask.jsonify({'success': 'OK'})
        else:
            abort(403, message=f"Access denied")


parser = reqparse.RequestParser()
parser.add_argument('api-key', required=True, type=str)
parser.add_argument('id', required=False, type=int)
parser.add_argument('lesson', required=True, type=int)
parser.add_argument('topic', required=True, type=str)
parser.add_argument('grade', required=True, type=str)
parser.add_argument('teacher', required=False, type=int)
parser.add_argument('cabinet', required=True, type=str)
parser.add_argument('start_date', required=True, type=str)
parser.add_argument('end_date', required=True, type=str)


class ReplacementsListResource(Resource):
    def get(self):
        args = parser_oneEl.parse_args()
        level = get_access_level(args['api-key'])
        session = db_session.create_session()
        if level == 3:
            replacements = session.query(Replacement).all()
            return flask.jsonify({'replacements': [item.to_dict(rules=('-user', '-lessons'))
                                                   for item in replacements]})
        if level == 2:
            teacher = session.query(User).filter(User.token == args['api-key']).first()
            replacements = session.query(Replacement).filter(Replacement.teacher == teacher.id)
            if replacements:
                return flask.jsonify({'replacements': [item.to_dict(rules=('-user', '-lessons'))
                                                       for item in replacements]})
            abort(403, message="Access denied")
        if level == 1:
            user = session.query(User).filter(User.token == args['api-key']).first()
            replacements = session.query(Replacement).filter(Replacement.grade == user.grade)
            if replacements:
                return flask.jsonify({'replacements': [item.to_dict(rules=('-user', '-lessons'))
                                                       for item in replacements]})
            abort(403, message="Access denied")

    def post(self):
        args = parser.parse_args()
        level = get_access_level(args['api-key'])
        if level == 3:
            session = db_session.create_session()
            replacements = Replacement(
                id=args['id'],
                lesson=args['lesson'],
                topic=args['topic'],
                grade=args['grade'],
                teacher=args['teacher'],
                cabinet=args['cabinet'],
                start_date=dt.strptime(args['start_date'], '%Y-%m-%d %H:%M:%S'),
                end_date=dt.strptime(args['end_date'], '%Y-%m-%d %H:%M:%S'),
            )
            session.add(replacements)
            session.commit()
            return flask.jsonify({'success': 'OK'})
        else:
            abort(403, message=f"Access denied")
