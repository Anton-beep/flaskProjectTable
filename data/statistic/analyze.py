from data.sqlalchemy import db_session
from data.models.users import User
from data.models.lessons import Lesson
from data.models.replacements import Replacement

import datetime
import csv


def analyze(interval, grade, level, user_id):
    db_sess = db_session.create_session()

    lessons = get_lessons(interval, grade, level, user_id)
    lessons = add_replacements(lessons, grade, level, user_id, interval)

    with open('static/time/time.csv', encoding="utf8") as csvfile:
        reader = list(csv.reader(csvfile, delimiter=';', quotechar='"'))

        start = float('inf')
        end = 0
        duration = reader[1][3]
        for les in lessons:
            if type(les) == Lesson:
                start = min(start, int(les.time.split('_')[0]))
                end = max(end, int(les.time.split('_')[0]))
    assert type(start) == type(end) == int
    param = {
        "start": reader[start][0], "end": reader[end][1],
        "duration_total": int(duration.split(':')[1]) * (end - start + 1),
        "duration_average": duration,
        "grade": ', '.join(list(set([item.grade for item in lessons]))),
        "lesson_total": len(lessons), "chart": {}, "days": {}, "teachers": {},
        "days_teachers": {full_name(db_sess.query(User).filter(User.id == user_id).first()): {}}
    }
    param = edit_chart(lessons, param, level, user_id, interval)

    return param


def get_lessons(interval, grade, level, user_id):
    db_sess = db_session.create_session()

    if level == 3:
        lessons = db_sess.query(Lesson).all()
    elif level == 2:
        lessons = db_sess.query(Lesson).filter(Lesson.teacher == user_id).all()
    else:
        lessons = db_sess.query(Lesson).filter(Lesson.grade == grade).all()

    if interval == 'day':
        day = datetime.datetime.now().strftime('%A').lower()
        lessons = list(filter(lambda x: day in x.time, lessons))

    return lessons


def add_replacements(lessons, grade, level, user_id, interval):
    db_sess = db_session.create_session()
    if level == 2:
        rep = db_sess.query(Replacement).filter(Replacement.teacher == user_id).all()
        lessons.extend(rep)

        to_dell = []
        for i, item in enumerate(lessons):
            rep = db_sess.query(Replacement).filter(Replacement.lesson == item.id).first()
            if rep is not None:
                if rep.start_date.day == datetime.datetime.now().day and interval == 'day':
                    to_dell.append(db_sess.query(Lesson).filter(Lesson.id == rep.lesson).first())
                elif interval == 'week':
                    to_dell.append(db_sess.query(Lesson).filter(Lesson.id == rep.lesson).first())
        for td in to_dell:
            try:
                del lessons[lessons.index(td)]
            except ValueError:
                pass
    else:
        for i, item in enumerate(lessons):
            rep = db_sess.query(Replacement).filter(Replacement.lesson == item.id).first()
            if rep is not None:
                if rep.start_date.day == datetime.datetime.now().day and interval == 'day' and (
                        level == 3 or grade == rep.grade):
                    lessons[i] = rep
                elif interval == "week" and (level == 3 or grade == rep.grade):
                    lessons[i] = rep
    return lessons


def edit_chart(lessons, param, level, user_id, interval):
    db_sess = db_session.create_session()

    for item in lessons:
        pie_chart = param["chart"].get(item.topic, 0)
        pie_chart += int(param["duration_average"].split(':')[1])

        if type(item) == Lesson:
            combo_chart = param["days"].get(item.time.split('_')[1], {})
            combo_chart[item.topic] = combo_chart.get(item.topic, 0) + 1
        else:
            day = db_sess.query(Lesson).filter(Lesson.id == item.lesson).first()
            combo_chart = param["days"].get(day.time.split('_')[1], {})
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
        if type(item) == Lesson:
            param["days"][item.time.split('_')[1]] = combo_chart
        else:
            day = db_sess.query(Lesson).filter(Lesson.id == item.lesson).first()
            param["days"][day.time.split('_')[1]] = combo_chart

    if level == 2:
        name = full_name(db_sess.query(User).filter(User.id == user_id).first())

        replace = db_sess.query(Replacement).filter(Replacement.teacher == user_id).all()
        if interval == 'day':
            replace = list(filter(lambda x: x.start_date.day ==
                                            datetime.datetime.now().day, replace))

        replaced = db_sess.query(Replacement).all()
        replaced = list(filter(lambda x: db_sess.query(Lesson).filter(
            Lesson.id == x.lesson, Lesson.teacher == user_id).first() is not None, replaced))
        if interval == 'day':
            replaced = list(filter(lambda x: x.start_date.day ==
                                            datetime.datetime.now().day, replaced))
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
