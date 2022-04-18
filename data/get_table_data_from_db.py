from sqlalchemy import or_

from data.models.lessons import Lesson
from data.models.replacements import Replacement
from data.models.users import User
from data.sqlalchemy import db_session


def rep_in_week(rep_start, rep_end, week_start, week_end):
    if rep_start <= week_end and rep_end >= week_start:
        return True
    return False


def table_data_for_user(grade, week) -> tuple:
    """returns header and rows"""
    header = ['Номер урока', 'Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота']
    rows = []

    db_sess = db_session.create_session()
    lessons_user = list(db_sess.query(Lesson).filter(Lesson.grade == grade))
    lessons_week = {
        'monday': {},
        'tuesday': {},
        'wednesday': {},
        'thursday': {},
        'friday': {},
        'saturday': {}
    }
    for lesson_grade in lessons_week:
        for lesson in sorted(filter(lambda x: x.time.split('_')[1] == lesson_grade, lessons_user),
                             key=lambda x: int(x.time.split('_')[0])):
            replacement = db_sess.query(Replacement).filter(Replacement.lesson == lesson.id).first()
            if replacement:
                if week[0] < replacement.end_date and week[1] > replacement.start_date:
                    lessons_week[lesson_grade][int(
                        lesson.time.split('_')[0])] = (
                        'replacementText', f'ЗАМЕНА {lesson.topic} НА {replacement.topic}' \
                                           f' В КАБИНЕТЕ {replacement.cabinet}')
            else:
                lessons_week[lesson_grade][
                    int(lesson.time.split('_')[0])] = lesson.topic + ' ' + lesson.cabinet

    min_count = min([min(el.keys(), default=1) for el in lessons_week.values()])
    max_count = max([max(el.keys(), default=1) for el in lessons_week.values()])

    for count in range(min_count, max_count + 1):
        rows.append([str(count)] + [el.get(count, '-') for el in lessons_week.values()])

    return header, rows


def table_data_for_teacher(teacher, week) -> tuple:
    """returns header and rows"""
    header = ['Номер урока', 'Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота']
    rows = []

    db_sess = db_session.create_session()
    lessons_teacher = list(db_sess.query(Lesson).filter(Lesson.teacher == teacher))
    replacements_teacher = list(db_sess.query(Replacement).filter(Replacement.teacher == teacher))
    lessons_week = {
        'monday': {},
        'tuesday': {},
        'wednesday': {},
        'thursday': {},
        'friday': {},
        'saturday': {}
    }
    for el in lessons_week:
        for lesson in sorted(filter(lambda x: x.time.split('_')[1] == el, lessons_teacher),
                             key=lambda x: int(x.time.split('_')[0])):
            lessons_week[el][int(lesson.time.split('_')[0])] = lesson.topic + ' ' + lesson.cabinet

        for replacement in sorted(
                filter(lambda x: x.lessons.time.split('_')[1] == el, replacements_teacher),
                key=lambda x: int(x.lessons.time.split('_')[0])):
            if week[0] < replacement.end_date and week[1] > replacement.start_date:
                lessons_week[el][
                    int(replacement.lessons.time.split('_')[
                            0])] = (
                    'replacementText', f'ЗАМЕНА У {replacement.grade} : ' + replacement.topic + \
                    ' ' + replacement.cabinet)

    min_count = min([min(el.keys(), default=1) for el in lessons_week.values()])
    max_count = max([max(el.keys(), default=1) for el in lessons_week.values()])

    for iter in range(min_count, max_count + 1):
        rows.append([str(iter)] + [el.get(iter, '-') for el in lessons_week.values()])

    return header, rows


def table_data_for_admin(week):
    """create table for admin"""
    db_sess = db_session.create_session()
    header = ['Номер урока'] + [teacher.surname + ' ' + teacher.name for teacher in list(
        db_sess.query(User).filter(or_(User.access_level == 2, User.access_level == 3)))]
    rows = []

    week_days = {
        'monday': 'понедельник',
        'tuesday': 'вторник',
        'wednesday': 'среда',
        'thursday': 'четверг',
        'friday': 'пятница'
    }
    lessons_admin = list(db_sess.query(Lesson))
    lessons_dict = {}
    for teacher in list(
            db_sess.query(User).filter(or_(User.access_level == 2, User.access_level == 3))):
        lessons_dict[teacher] = db_sess.query(Lesson).filter(Lesson.teacher == teacher.id)

    min_count = min([int(el.time.split('_')[0]) for el in lessons_admin])
    max_count = max([int(el.time.split('_')[0]) for el in lessons_admin])

    all_replacements = list(db_sess.query(Replacement))

    for week_day in week_days:
        for iter in range(min_count, max_count + 1):
            new_row = [str(iter) + ' ' + week_days[week_day]]
            for teacher in list(
                    db_sess.query(User).filter(
                        or_(User.access_level == 2, User.access_level == 3))):
                lessons_iter = list(filter(
                    lambda x: x.time.split('_')[0] == str(iter) and x.time.split('_')[
                        1] == week_day, lessons_dict[teacher]))
                # find rep
                rep = None
                replacements = list(
                    db_sess.query(Replacement).filter(Replacement.teacher == teacher.id))
                for replacement in replacements:
                    lesson = db_sess.query(Lesson).filter(Lesson.id == replacement.lesson).first()
                    if lesson:
                        if lesson.time == f'{iter}_{week_day}':
                            rep = replacement
                            break
                if rep and rep_in_week(rep.start_date, rep.end_date, week[0], week[1]):
                    new_row += [('replacementText',
                                 f'ЗАМЕНА {rep.grade} '
                                 f'{rep.topic} {rep.cabinet}')]
                else:
                    if len(lessons_iter) > 0:
                        flag_lesson = True
                        replacements_lesson = db_sess.query(Replacement).filter(
                            Replacement.lesson == lessons_iter[0].id)
                        for rep in replacements_lesson:
                            if rep_in_week(rep.start_date, rep.end_date, week[0], week[1]):
                                flag_lesson = False
                                break
                        if flag_lesson:
                            new_row += [
                                f'{lessons_iter[0].grade} {lessons_iter[0].topic} '
                                f'{lessons_iter[0].cabinet}']
                    else:
                        new_row += ['-']
            rows.append(new_row)
    return header, rows
