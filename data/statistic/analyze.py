from data.sqlalchemy import db_session
from data.models.users import User
from data.models.lessons import Lesson
from data.models.replacements import Replacement

import datetime


def analyze(date, grade, level, user_id):
    db_sess = db_session.create_session()

    lessons = get_lessons(date, grade, level, user_id)
    lessons = add_replacements(lessons, grade, level, user_id, date)

    start = [x.start_date.time() for x in lessons]
    end = [x.end_date.time() for x in lessons]
    param = {
        "start": str(min(start)),
        "end": str(max(end)),
        "duration_total": str(datetime.timedelta(seconds=60 * sum(
            [60 * end[i].hour + end[i].minute - 60 * start[i].hour - start[i].minute
             for i in range(len(end))]))),
        "duration_average": str(datetime.timedelta(seconds=sum([int(
            (x.end_date - x.start_date).seconds) for x in lessons]) / len(lessons))),
        "grade": ', '.join(list(set([item.grade for item in lessons]))),
        "lesson_total": len(lessons), "chart": {}, "days": {}, "teachers": {},
        "days_teachers": {full_name(db_sess.query(User).filter(User.id == user_id).first()): {}}
    }

    param = edit_chart(lessons, param, level, user_id, date)

    return param


def get_lessons(date, grade, level, user_id):
    db_sess = db_session.create_session()

    if level == 3:
        lessons = db_sess.query(Lesson).all()
    elif grade is None:
        lessons = db_sess.query(Lesson).filter(Lesson.teacher == user_id)
    else:
        lessons = db_sess.query(Lesson).filter(Lesson.grade == grade).all()

    if type(date) == range:
        lessons = list(filter(lambda x: x.start_date.day in date, lessons))
    elif type(date) == int:
        lessons = list(filter(lambda x: x.start_date.day == date, lessons))
    else:
        lessons = list(filter(lambda x: x.start_date.month == date[0], lessons))

    return lessons


def add_replacements(lessons, grade, level, user_id, date):
    db_sess = db_session.create_session()
    if grade is None and level == 2:
        rep = db_sess.query(Replacement).filter(Replacement.teacher == user_id).all()
        lessons.extend(rep)
    else:
        for i, item in enumerate(lessons):
            rep = db_sess.query(Replacement).filter(Replacement.lesson == item.id).first()
            if rep is not None:
                lessons[i] = rep
    if type(date) == range:
        lessons = list(filter(lambda x: x.start_date.day in date, lessons))
    elif type(date) == int:
        lessons = list(filter(lambda x: x.start_date.day == date, lessons))
    else:
        lessons = list(filter(lambda x: x.start_date.month == date[0], lessons))
    return lessons


def edit_chart(lessons, param, level, user_id, date):
    db_sess = db_session.create_session()
    for item in lessons:
        pie_chart = param["chart"].get(item.topic, 0)
        pie_chart += item.end_date.time().hour * 60 + item.end_date.time().minute \
                - item.start_date.time().hour * 60 - item.start_date.time().minute

        combo_chart = param["days"].get(item.start_date.day, {})
        combo_chart[item.topic] = combo_chart.get(item.topic, 0) + 1

        if type(item) == Replacement:
            teacher = item.teacher
            teacher = full_name(db_sess.query(User).filter(User.id == teacher).first())
            replace = param["teachers"].get(teacher, {"replace": 0, "replaced": 0})
            replace["replace"] += 1

            replacing = db_sess.query(Lesson).filter(Lesson.id == item.lesson).first().teacher
            replacing = full_name(db_sess.query(User).filter(User.id == replacing).first())
            replaced = param["teachers"].get(replacing, {"replace": 0, "replaced": 0})
            replaced["replaced"] += 1

            param["teachers"][teacher] = replace
            param["teachers"][replacing] = replaced

        param["chart"][item.topic] = pie_chart
        param["days"][item.start_date.day] = combo_chart

    if level == 2:
        name = full_name(db_sess.query(User).filter(User.id == user_id).first())

        replace = db_sess.query(Replacement).filter(Replacement.teacher == user_id).all()
        if type(date) == range:
            replace = list(filter(lambda x: x.start_date.day in date, replace))
        elif type(date) == int:
            replace = list(filter(lambda x: x.start_date.day == date, replace))
        else:
            replace = list(filter(lambda x: x.start_date.month == date[0], replace))

        replaced = db_sess.query(Replacement).all()
        replaced = list(filter(lambda x: db_sess.query(Lesson).filter(
            Lesson.id == x.lesson, Lesson.teacher == user_id).first() is not None, replaced))
        if type(date) == range:
            replaced = list(filter(lambda x: x.start_date.day in date, replaced))
        elif type(date) == int:
            replaced = list(filter(lambda x: x.start_date.day == date, replaced))
        else:
            replaced = list(filter(lambda x: x.start_date.month == date[0], replaced))
        for item in replace:
            day = item.start_date.day
            rep = param["days_teachers"][name].get(day, {"replace": 0, "replaced": 0})
            rep["replace"] += 1
            param["days_teachers"][name][day] = rep
        for item in replaced:
            day = item.start_date.day
            rep = param["days_teachers"][name].get(day, {"replace": 0, "replaced": 0})
            rep["replaced"] += 1
            param["days_teachers"][name][day] = rep

    return param


def full_name(user):
    return ' '.join([user.surname, user.name, user.patronymic])
