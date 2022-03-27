import os
import datetime
from random import choice, randrange
from calendar import monthrange as mth
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
    user.surname, user.name, user.patronymic = 'Darkholme', 'Van', 'Dungeon Master'
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

    user = User()
    user.surname, user.name, user.patronymic = 'Pcholka', 'Anton', 'Zhzhzhz'
    user.email = 'pchola@bee.bzz'
    user.set_password('pchola')
    user.access_level = 2
    user.token = 'teacher3'  # Надо изменить
    db_sess.add(user)

    user = User()
    user.surname, user.name, user.patronymic = 'teacher4', 'teacher4', 'teacher4'
    user.email = 'teacher@4'
    user.set_password('teacher4')
    user.access_level = 2
    user.token = 'teacher4'  # Надо изменить
    db_sess.add(user)

    user = User()
    user.surname, user.name, user.patronymic = 'teacher5', 'teacher5', 'teacher5'
    user.email = 'teacher@5'
    user.set_password('teacher5')
    user.access_level = 2
    user.token = 'teacher5'  # Надо изменить
    db_sess.add(user)

    db_sess.commit()


def add_lessons(flag):
    if not flag:
        return
    db_sess = db_session.create_session()

    lesson = Lesson()
    lesson.topic = 'Алгебра'
    lesson.grade = '9Ф'
    lesson.teacher = 4
    lesson.cabinet = 'Gym'
    lesson.start_date = datetime.datetime(2022, 3, 14, 15, 0, 0, 0)
    lesson.end_date = datetime.datetime(2022, 3, 14, 15, 40, 0, 0)
    db_sess.add(lesson)

    lesson = Lesson()
    lesson.topic = 'Геометрия'
    lesson.grade = '9Ж'
    lesson.teacher = 4
    lesson.cabinet = 'Gym'
    lesson.start_date = datetime.datetime(2022, 3, 24, 12, 10, 0, 0)
    lesson.end_date = datetime.datetime(2022, 3, 24, 12, 40, 0, 0)
    db_sess.add(lesson)

    lesson = Lesson()
    lesson.topic = 'Геометрия'
    lesson.grade = '9Ж'
    lesson.teacher = 5
    lesson.cabinet = 'Gym'
    lesson.start_date = datetime.datetime(2022, 3, 24, 13, 00, 0, 0)
    lesson.end_date = datetime.datetime(2022, 3, 24, 13, 35, 0, 0)
    db_sess.add(lesson)

    lesson = Lesson()
    lesson.topic = 'Химия'
    lesson.grade = '9Ж'
    lesson.teacher = 5
    lesson.cabinet = 'Gym'
    lesson.start_date = datetime.datetime(2022, 3, 24, 15, 20, 0, 0)
    lesson.end_date = datetime.datetime(2022, 3, 24, 16, 20, 0, 0)
    db_sess.add(lesson)

    lesson = Lesson()
    lesson.topic = 'Варка пельменей. Много мяса, мало теста'
    lesson.grade = '9Ж'
    lesson.teacher = 5
    lesson.cabinet = 'Столовая'
    lesson.start_date = datetime.datetime(2022, 3, 26, 16, 50, 0, 0)
    lesson.end_date = datetime.datetime(2022, 3, 26, 17, 25, 0, 0)
    db_sess.add(lesson)

    lesson = Lesson()
    lesson.topic = 'Химия'
    lesson.grade = '9Ф'
    lesson.teacher = 4
    lesson.cabinet = 'Gym'
    lesson.start_date = datetime.datetime(2022, 3, 21, 17, 30, 0, 0)
    lesson.end_date = datetime.datetime(2022, 3, 21, 18, 20, 0, 0)
    db_sess.add(lesson)

    lesson = Lesson()
    lesson.topic = 'Электив Химия'
    lesson.grade = '9Ф'
    lesson.teacher = 4
    lesson.cabinet = 'Gym'
    lesson.start_date = datetime.datetime(2022, 3, 24, 18, 30, 0, 0)
    lesson.end_date = datetime.datetime(2022, 3, 24, 19, 40, 0, 0)
    db_sess.add(lesson)

    lesson = Lesson()
    lesson.topic = 'Химия'
    lesson.grade = '9Ф'
    lesson.teacher = 4
    lesson.cabinet = 'Gym'
    lesson.start_date = datetime.datetime(2022, 3, 26, 20, 0, 0, 0)
    lesson.end_date = datetime.datetime(2022, 3, 26, 20, 20, 0, 0)
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
    rep.teacher = 5
    rep.cabinet = 'Столовая'
    rep.start_date = datetime.datetime(2022, 3, 24, 16, 0, 0, 0)
    rep.end_date = datetime.datetime(2022, 3, 24, 16, 40, 0, 0)
    db_sess.add(rep)

    db_sess.commit()


def add_random(flag, lessons, replacements):
    if not flag:
        return

    db_sess = db_session.create_session()

    topics = ["Алгебра", "Геометрия", "Биология", "Химия", "География", "Физика", "Обществозание",
              "Варка пельменей", "Информатика"]
    grades = ['9Ф', '9Ж']
    teachers = [4, 5, 6, 7, 8]

    for i in range(lessons):
        lesson = Lesson()
        lesson.topic = choice(topics)
        lesson.grade = choice(grades)
        lesson.teacher = choice(teachers)
        lesson.cabinet = f'{choice(["А", "B", "С"])}{randrange(100, 120)}'

        now = datetime.datetime.now()

        day = randrange(*mth(now.year, now.month))
        hour = randrange(8, 20)
        minute = randrange(0, 50)
        duration = randrange(30, 50)

        lesson.start_date = datetime.datetime(2022, 3, day, hour, minute, 0, 0)
        if minute + duration < 60:
            lesson.end_date = datetime.datetime(2022, 3, day, hour, minute + duration, 0, 0)
        else:
            lesson.end_date = datetime.datetime(2022, 3, day, hour + 1,
                                                minute + duration - 60, 0, 0)
        db_sess.add(lesson)

    for i in range(replacements):
        rep = Replacement()
        rep.topic = choice(topics)
        rep.grade = choice(grades)
        rep.cabinet = f'{choice(["А", "B", "С"])}{randrange(100, 120)}'

        while True:
            less_id = randrange(1, lessons)
            if db_sess.query(Replacement).filter(Replacement.lesson == less_id).first() is None:
                break
        less = db_sess.query(Lesson).filter(Lesson.id == less_id).first()
        new_teachers = teachers.copy()
        new_teachers.remove(less.teacher)

        rep.lesson = less.id
        rep.teacher = choice(new_teachers)

        rep.start_date = less.start_date
        rep.end_date = less.end_date
        db_sess.add(rep)

    db_sess.commit()
