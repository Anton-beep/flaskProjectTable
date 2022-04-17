from sqlalchemy import and_

from data.models.lessons import Lesson
from data.models.replacements import Replacement
from data.models.users import User
from data.sqlalchemy import db_session


def convert_table_text_to_time(time_table: str):
    """convert site table format to python"""
    convert_dict = {
        'понедельник': 'monday',
        'вторник': 'tuesday',
        'среда': 'wednesday',
        'четверг': 'thursday',
        'пятница': 'friday',
        'суббота': 'saturday',
        'воскресенье': 'sunday'
    }
    count, week_day = time_table.split()
    return f'{count}_{convert_dict[week_day]}'


def edit_write_replacement(data, form, table_week):
    replacement_to_edit = None
    db_sess = db_session.create_session()
    teacher = db_sess.query(User).filter(
        User.name == data['teacher'].split()[1],
        User.surname == data['teacher'].split()[0]).first()
    time_db = convert_table_text_to_time(data['time'])
    # find lessons
    teacher_old = db_sess.query(User).filter(
        User.name == data['rep_teacher'].split()[1],
        User.surname == data['rep_teacher'].split()[0]).first()
    lesson_rep = db_sess.query(Lesson).filter(
        and_(Lesson.time == time_db, Lesson.teacher == teacher_old.id)).first()
    lessons_time = db_sess.query(Lesson).filter(Lesson.time == time_db)
    if lessons_time:
        lessons_time_id = [element.id for element in lessons_time]
        for lesson_id in lessons_time_id:
            replacement_to_edit = db_sess.query(Replacement).filter(
                and_(Replacement.teacher == teacher_old.id,
                     Replacement.lesson == lesson_id)).first()
            if replacement_to_edit:
                break

    if replacement_to_edit:
        replacement_to_edit.topic = form.topic.data
        replacement_to_edit.grade = form.grade.data
        replacement_to_edit.cabinet = form.cabinet.data
        replacement_to_edit.teacher = teacher.id
    else:
        replacement = Replacement()
        replacement.topic = form.topic.data
        replacement.grade = form.grade.data
        replacement.cabinet = form.cabinet.data
        replacement.time = time_db
        replacement.teacher = teacher.id
        replacement.start_date = table_week[0]
        replacement.end_date = table_week[1]
        replacement.lesson = lesson_rep.id
        db_sess.add(replacement)
    db_sess.commit()


def edit_write_lesson(data, form):
    # lesson
    db_sess = db_session.create_session()
    time_db = convert_table_text_to_time(data['time'])
    teacher = db_sess.query(User).filter(
        User.name == data['teacher'].split()[1],
        User.surname == data['teacher'].split()[0]).first()
    lesson_to_edit = db_sess.query(Lesson).filter(
        and_(Lesson.time == time_db, Lesson.teacher == teacher.id)).first()
    if lesson_to_edit:
        lesson_to_edit.topic = form.topic.data
        lesson_to_edit.grade = form.grade.data
        lesson_to_edit.cabinet = form.cabinet.data
    else:
        lesson = Lesson()
        lesson.topic = form.topic.data
        lesson.grade = form.grade.data.upper()
        lesson.cabinet = form.cabinet.data
        lesson.time = time_db
        lesson.teacher = teacher.id
        db_sess.add(lesson)
    db_sess.commit()
