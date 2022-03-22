import flask
from flask_restful import abort, Resource, reqparse
from data.sqlalchemy import db_session
from data.models.users import User

from datetime import datetime as dt


def abort_if_users_not_found(users_id):
    session = db_session.create_session()
    news = session.query(User).get(users_id)
    if not news:
        abort(404, message=f"User {users_id} not found")


class UsersResource(Resource):
    def get(self, users_id):
        abort_if_users_not_found(users_id)
        session = db_session.create_session()
        users = session.query(User).get(users_id)
        return flask.jsonify({'users': users.to_dict()})

    def delete(self, users_id):
        abort_if_users_not_found(users_id)
        session = db_session.create_session()
        users = session.query(User).get(users_id)
        session.delete(users)
        session.commit()
        return flask.jsonify({'success': 'OK'})


parser = reqparse.RequestParser()
parser.add_argument('id', required=False, type=int)
parser.add_argument('name', required=True, type=str)
parser.add_argument('surname', required=True, type=str)
parser.add_argument('patronymic', required=False, type=str)
parser.add_argument('grade', required=True, type=str)
parser.add_argument('email', required=True, type=str)
parser.add_argument('hashed_password', required=True, type=str)
parser.add_argument('modified_date', required=True, type=str)
parser.add_argument('access_level', required=True, type=int)
parser.add_argument('token', required=True, type=str)


class UserListResource(Resource):
    def get(self):
        session = db_session.create_session()
        users = session.query(User).all()
        return flask.jsonify({'users': [item.to_dict()
                                        for item in users]})

    def post(self):
        args = parser.parse_args()
        session = db_session.create_session()
        users = User(
            id=args['id'],
            name=args['name'],
            surname=args['surname'],
            patronymic=args['patronymic'],
            grade=args['grade'],
            email=args['email'],
            hashed_password=args['hashed_password'],
            modified_date=dt.strptime(args['modified_date'], '%Y-%m-%d %H:%M:%S'),
            access_level=args['access_level'],
            token=args['token']
        )
        session.add(users)
        session.commit()
        return flask.jsonify({'success': 'OK'})