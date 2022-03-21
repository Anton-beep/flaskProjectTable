from flask import Flask

from data.sqlalchemy import db_session

import init

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'


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
