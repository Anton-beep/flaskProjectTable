from flask import Flask
from flask_restful import Api

from data.sqlalchemy import db_session
from data.API_resources import users_resources

import init

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

db_session.global_init('db/timetable.db')

api = Api(app)

api.add_resource(users_resources.UserListResource, '/api/users')
api.add_resource(users_resources.UsersResource, '/api/users/<int:users_id>')


def main():
    init.clear(True)

    db_session.global_init("db/timetable.db")

    init.fill_table(admin=True, users=True, lessons=False, replacements=False)

    app.run()


@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'


if __name__ == '__main__':
    main()
