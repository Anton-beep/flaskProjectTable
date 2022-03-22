import os
import datetime
from data.sqlalchemy import db_session
from data.models.users import User
from data.models.lessons import Lesson
from data.models.replacements import Replacement


def clear(flag):
    if not flag:
        return

    try:
        os.remove('db/timetable.db')
    except FileNotFoundError:
        pass


def fill_table(admin=False, users=False, lessons=False, replacements=False):
    add_admin(admin)
    add_users(users)
    add_lessons(lessons)
    add_replacements(replacements)


def add_admin(flag):
    if not flag:
        return

    db_sess = db_session.create_session()

    user = User()
    user.surname, user.name, user.patronymic = 'Чернова', 'Елена', 'Викторовна'
    user.email = 'admin@tbl.ru'
    user.set_password('admin')
    user.access_level = 3
    user.token = 'admin'  # Надо изменить

    db_sess.add(user)
    db_sess.commit()


def add_users(flag):
    if not flag:
        return

    db_sess = db_session.create_session()

    user = User()
    user.surname, user.name, user.patronymic = 'Лебедев', 'Федор', 'Михайлович'
    user.grade = '9Ф'
    # user.email = 'dr_pepper228@clown.py'
    # user.set_password('bib')
    user.access_level = 1
    user.token = 'student1'  # Надо изменить
    db_sess.add(user)

    user = User()
    user.surname, user.name, user.patronymic = 'Жабов', 'Жаба', 'Жабович'
    user.grade = '9Ж'
    user.email = 'lyaguha@frog.kva'
    user.set_password('i_love_frogs')
    user.access_level = 1
    user.token = 'student2'  # Надо изменить
    db_sess.add(user)

    user = User()
    user.surname, user.name = 'Darkholme', 'Van'
    user.email = 'dungen@master.gachi'
    user.set_password('fisting_is_300')
    user.access_level = 2
    user.token = 'teacher1'  # Надо изменить
    db_sess.add(user)

    user = User()
    user.surname, user.name, user.patronymic = 'Пельменев', 'Floppa', 'Котов'
    user.email = 'floppa@cat.meow'
    user.set_password('pelmeni')
    user.access_level = 2
    user.token = 'teacher2'  # Надо изменить
    db_sess.add(user)

    db_sess.commit()


def add_lessons(flag):
    if not flag:
        return
    db_sess = db_session.create_session()

    lesson = Lesson()
    lesson.topic = 'Алгебра'
    lesson.grade = '9Ф'
    lesson.teacher = 1
    lesson.cabinet = 'Gym'
    lesson.start_date = datetime.datetime(2022, 3, 27, 15, 0, 0, 0)
    lesson.end_date = datetime.datetime(2022, 3, 27, 15, 40, 0, 0)
    db_sess.add(lesson)

    lesson = Lesson()
    lesson.topic = 'Геометрия'
    lesson.grade = '9Ж'
    lesson.teacher = 1
    lesson.cabinet = 'Gym'
    lesson.start_date = datetime.datetime(2022, 3, 27, 15, 55, 0, 0)
    lesson.end_date = datetime.datetime(2022, 3, 27, 16, 35, 0, 0)
    db_sess.add(lesson)

    db_sess.commit()


def add_replacements(flag):
    if not flag:
        return

    db_sess = db_session.create_session()

    rep = Replacement()
    rep.lesson = 2
    rep.topic = 'Информатика'
    rep.grade = '9Ж'
    rep.teacher = 2
    rep.cabinet = 'Столовая'
    rep.start_date = datetime.datetime(2022, 3, 27, 16, 0, 0, 0)
    rep.end_date = datetime.datetime(2022, 3, 27, 16, 40, 0, 0)
    db_sess.add(rep)

    db_sess.commit()
