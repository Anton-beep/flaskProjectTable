"""main"""
import csv
import os
import datetime
import secrets
from pprint import pprint

import PIL

from flask import Flask, redirect, render_template, request, send_file
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from flask_restful import abort, Api
from sqlalchemy import or_, and_
from werkzeug.utils import secure_filename
import xlsxwriter

from data.sqlalchemy import db_session
from data.models.users import User
from data.models.lessons import Lesson
from data.models.replacements import Replacement
from data.statistic import GoogleCharts, analyze
from data.API_resources import users_resources
from data.API_resources import lessons_resources
from data.API_resources import replacements_resources

from forms.login import LoginForm
from forms.register import RegisterForm
from forms.register_admin import RegisterAdminForm
from forms.token_check import TokenForm
from forms.edit_lesson import EditLessonForm
from forms.edit_users import EditUsersForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'Church_Of_Saint_Floppa'

# init.clear(True)
db_session.global_init("db/timetable.db")
# init.fill_table(admin=True, users=True, lessons=False, replacements=False)
# init.add_random(True, 150, 40)

api = Api(app)
# users api
api.add_resource(users_resources.UserListResource, '/api/users')
api.add_resource(users_resources.UsersResource, '/api/users/<int:users_id>')

# lessons api
api.add_resource(lessons_resources.LessonsListResource, '/api/lessons')
api.add_resource(lessons_resources.LessonsResource, '/api/lessons/<int:lessons_id>')

# replacements api
api.add_resource(replacements_resources.ReplacementsListResource, '/api/replacements')
api.add_resource(replacements_resources.ReplacementsResource,
                 '/api/replacements/<int:replacements_id>')

login_manager = LoginManager()
login_manager.init_app(app)


@app.route('/', methods=['POST', 'GET'])
def base():
    """view table"""
    global now_day, table_week
    rows = []
    header = []
    form = None
    form_replacement = None

    if current_user.is_authenticated:
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.id == current_user.id).first()

        form = EditLessonForm()
        if form.validate_on_submit() and user.access_level == 3:
            data = request.form
            if data:
                if data['title'] == 'Изменение/Создание замены':
                    # reaplacement
                    teacher = db_sess.query(User).filter(
                        User.name == data['teacher'].split()[1],
                        User.surname == data['teacher'].split()[0]).first()
                    time_db = convert_table_text_to_time(data['time'])
                    # find lessons
                    lessons_time = db_sess.query(Lesson).filter(
                        Lesson.time == time_db
                    )
                    replacements_time = list()
                    bib = list(lessons_time)
                    for lesson in lessons_time:
                        rep = db_sess.query(Replacement).filter(
                            Replacement.lesson == lesson.id).first()
                        if rep:
                            replacements_time.append(rep)
                    replacement_to_edit = None
                    if replacements_time:
                        for replacement in replacements_time:
                            if replacement.teacher == teacher.id:
                                replacement_to_edit = replacement
                                break

                    if replacement_to_edit:
                        replacement_to_edit.topic = form.topic.data
                        replacement_to_edit.grade = form.grade.data
                        replacement_to_edit.cabinet = form.cabinet.data
                    else:
                        replacement = Replacement()
                        replacement.topic = form.topic.data
                        replacement.grade = form.grade.data
                        replacement.cabinet = form.cabinet.data
                        replacement.time = time_db
                        replacement.teacher = teacher.id
                        replacement.start_date = table_week[0]
                        replacement.end_date = table_week[1]
                        # find lesson without reps
                        for lesson in lessons_time:
                            if db_sess.query(Replacement).filter(
                                    Replacement.lesson == lesson.id).first() is None:
                                replacement.lesson = lesson.id
                                break
                        db_sess.add(replacement)
                    db_sess.commit()
                else:
                    # lesson
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
                        lesson.grade = form.grade.data
                        lesson.cabinet = form.cabinet.data
                        lesson.time = time_db
                        lesson.teacher = teacher.id
                        db_sess.add(lesson)
                    db_sess.commit()
        elif request.method == 'POST' and user.access_level == 3:
            data = request.json
            if data['message'] == 'delete lesson':
                teacher = db_sess.query(User).filter(
                    User.name == data['teacher'].split()[1],
                    User.surname == data['teacher'].split()[0]).first()
                time_db = convert_table_text_to_time(data['time'])
                lesson_to_del = db_sess.query(Lesson).filter(
                    and_(Lesson.time == time_db, Lesson.teacher == teacher.id)).first()
                db_sess.delete(lesson_to_del)
                db_sess.commit()
            elif data['message'] == 'delete replacement':
                teacher = db_sess.query(User).filter(
                    User.name == data['teacher'].split()[1],
                    User.surname == data['teacher'].split()[0]).first()
                time_db = convert_table_text_to_time(data['time'])
                lesson_to_del = db_sess.query(Lesson).filter(
                    and_(Lesson.time == time_db, Lesson.teacher == teacher.id)).first()
                db_sess.delete(lesson_to_del)
                db_sess.commit()
            elif data['message'] == 'new week':
                now_day = datetime.datetime.strptime(data['day'], '%Y-%m-%d')
                table_week = get_week_from_day(now_day)
                now_day = now_day.strftime('%Y-%m-%d')

        if user.access_level == 1:
            header, rows = table_data_for_user(user.grade, table_week)
        elif user.access_level == 2:
            header, rows = table_data_for_teacher(user.id, table_week)
        elif user.access_level == 3:
            header, rows = table_data_for_admin(table_week)

    return render_template("show_table.html", rows=rows, header=header, form=form,
                           form_replacement=form_replacement, now_day=now_day)


@app.route('/users', methods=['POST', 'GET'])
def users():
    if current_user.access_level == 3:
        form = EditUsersForm()

        db_sess = db_session.create_session()

        if form.validate_on_submit():
            user_to_edit = db_sess.query(User).filter(User.id == int(form.id.data)).first()
            if form.token.data != '':
                user_to_edit.token = form.token.data
            if form.grade.data != '':
                user_to_edit.grade = form.grade.data
            if form.access_level.data != '':
                user_to_edit.access_level = form.access_level.data
            if form.surname.data != '':
                user_to_edit.surname = form.surname.data
            if form.name.data != '':
                user_to_edit.name = form.name.data
            if form.patronymic.data != '':
                user_to_edit.patronymic = form.patronymic.data
            if form.email.data != '':
                user_to_edit.email = form.email.data
            db_sess.add(user_to_edit)
            db_sess.commit()

        elif request.method == 'POST' and current_user.access_level == 3:
            data = request.json
            if data['message'] == 'delete user':
                user_to_del = db_sess.query(User).filter(User.id == int(data['user'])).first()
                db_sess.delete(user_to_del)
                db_sess.commit()

        header, rows = all_users_table()
        return render_template("all_users.html", rows=rows, header=header, form=form)
    abort(403, message="Access denied")


def all_users_table():
    """returns header and rows with all users"""
    header = ['id', 'имя', 'фамилия', 'отчество', 'класс', 'email', 'уровень доступа',
              'токен (ключ)']

    db_sess = db_session.create_session()
    users = list(db_sess.query(User))
    rows = list()
    for user in users:
        row = [user.id, user.name, user.surname, user.patronymic, user.grade, user.email,
               user.access_level, user.token]
        row = ['-' if el is None else el for el in row]
        rows.append(row)

    return header, rows


def convert_table_text_to_time(time_table: str):
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


def get_week_from_day(day):
    week_num = day.weekday()
    start_week_day = day - datetime.timedelta(days=week_num)
    end_week_day = start_week_day + datetime.timedelta(days=6)
    return start_week_day, end_week_day


now_day = datetime.datetime.today().strftime('%Y-%m-%d')
table_week = get_week_from_day(datetime.datetime.today())


@app.route('/register', methods=['POST', 'GET'])
def admin_register():
    """admin registers new users"""
    if current_user.is_authenticated:
        form = RegisterAdminForm()

        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.id == current_user.id).first()
        if user.access_level == 3:
            if form.validate_on_submit():
                # check new user in db
                set_users = set(db_sess.query(User))
                if form.grade.data:
                    grade_users = db_sess.query(User).filter(User.grade == form.grade.data)
                    if grade_users:
                        set_users = set(grade_users) & set_users
                if form.surname.data:
                    surname_users = db_sess.query(User).filter(
                        User.grade == form.surname.data)
                    if surname_users:
                        set_users = set(surname_users) & set_users
                if form.name.data:
                    name_users = db_sess.query(User).filter(User.name == form.name.data)
                    if name_users:
                        set_users = set(name_users) & set_users
                if form.patronymic.data:
                    patronymic_users = db_sess.query(User).filter(
                        User.patronymic == form.patronymic.data)
                    if patronymic_users:
                        set_users = set(patronymic_users) & set_users
                if form.email.data:
                    email_users = set(db_sess.query(User).filter(User.email == form.email.data))
                    if email_users:
                        set_users = set(email_users) & set_users
                if len(set_users) > 0:
                    message = 'Такой пользователь уже есть'
                elif form.email.data and email_users:
                    message = 'Пользователь с такой же почтой уже существует'
                else:
                    # generate token for new user and write in db

                    user = User()
                    if form.name.data:
                        user.name = form.name.data
                    if form.surname.data:
                        user.surname = form.surname.data
                    if form.patronymic.data:
                        user.patronymic = form.patronymic.data
                    if form.grade.data:
                        user.grade = form.grade.data
                    if form.email.data:
                        user.email = form.email.data
                    user.access_level = form.access_level.data

                    token = secrets.token_urlsafe(32)
                    user.token = token
                    db_sess.add(user)
                    db_sess.commit()
                    message = f'Токен этого пользователя: {token}'
                return render_template('register_admin.html', form=form, message=message)
        # render register form
        return render_template('register_admin.html', form=form)
    abort(403, message="Access denied")


@app.route('/download_table')
def download_table():
    """downloads user's table"""
    if current_user.is_authenticated:
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.id == current_user.id).first()

        if user.access_level == 1:
            header, rows = table_data_for_user(user.grade, table_week)
        elif user.access_level == 2:
            header, rows = table_data_for_teacher(user.id, table_week)
        elif user.access_level == 3:
            header, rows = table_data_for_admin(table_week)

        workbook = xlsxwriter.Workbook('test.xlsx')
        worksheet = workbook.add_worksheet()

        rows = [header] + rows

        for i in range(len(rows)):
            for j in range(len(rows[i])):
                if isinstance(rows[i][j], tuple):
                    if rows[i][j][0] == 'replacementText':
                        style = {'bg_color': 'orange'}
                    worksheet.write_string(i, j, rows[i][j][1], workbook.add_format(style))
                    worksheet.set_column(i, j, 20)
                else:
                    worksheet.write_string(i, j, rows[i][j])
                    worksheet.set_column(i, j, 20)
        workbook.close()

        return send_file('test.xlsx')
    else:
        abort(404)


def style_excel(val):
    style = f""""""
    if 'ЗАМЕНА' in val.split():
        style += ' background-color: orange;'
    return style


def table_data_for_user(grade, week) -> tuple:
    """returns header and rows"""
    header = ['Номер урока', 'Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота']
    rows = list()

    db_sess = db_session.create_session()
    lessons_user = list(db_sess.query(Lesson).filter(Lesson.grade == grade))
    lessons_week = {
        'monday': dict(),
        'tuesday': dict(),
        'wednesday': dict(),
        'thursday': dict(),
        'friday': dict(),
        'saturday': dict()
    }
    for el in lessons_week.keys():
        for lesson in sorted(filter(lambda x: x.time.split('_')[1] == el, lessons_user),
                             key=lambda x: int(x.time.split('_')[0])):
            replacement = db_sess.query(Replacement).filter(Replacement.lesson == lesson.id).first()
            if replacement:
                if week[0] < replacement.end_date and week[1] > replacement.start_date:
                    lessons_week[el][int(
                        lesson.time.split('_')[0])] = (
                        'replacementText', f'ЗАМЕНА {lesson.topic} НА {replacement.topic}' \
                                           f' В КАБИНЕТЕ {replacement.cabinet}')
            else:
                lessons_week[el][
                    int(lesson.time.split('_')[0])] = lesson.topic + ' ' + lesson.cabinet

    min_count = min([min(el.keys(), default=1) for el in lessons_week.values()])
    max_count = max([max(el.keys(), default=1) for el in lessons_week.values()])

    for iter in range(min_count, max_count + 1):
        rows.append([str(iter)] + [el.get(iter, '-') for el in lessons_week.values()])

    return header, rows


def table_data_for_teacher(teacher, week) -> tuple:
    """returns header and rows"""
    header = ['Номер урока', 'Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота']
    rows = list()

    db_sess = db_session.create_session()
    lessons_teacher = list(db_sess.query(Lesson).filter(Lesson.teacher == teacher))
    replacements_teacher = list(db_sess.query(Replacement).filter(Replacement.teacher == teacher))
    lessons_week = {
        'monday': dict(),
        'tuesday': dict(),
        'wednesday': dict(),
        'thursday': dict(),
        'friday': dict(),
        'saturday': dict()
    }
    for el in lessons_week.keys():
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
    db_sess = db_session.create_session()
    header = ['Номер урока'] + [teacher.surname + ' ' + teacher.name for teacher in list(
        db_sess.query(User).filter(or_(User.access_level == 2, User.access_level == 3)))]
    rows = list()

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

    for week_day in week_days.keys():
        for iter in range(min_count, max_count + 1):
            new_row = [str(iter) + ' ' + week_days[week_day]]
            for teacher in list(
                    db_sess.query(User).filter(
                        or_(User.access_level == 2, User.access_level == 3))):
                lessons_iter = list(filter(
                    lambda x: x.time.split('_')[0] == str(iter) and x.time.split('_')[
                        1] == week_day, lessons_dict[teacher]))
                if len(lessons_iter) > 0:
                    replacement = db_sess.query(Replacement).filter(Replacement.lesson ==
                                                                    lessons_iter[0].id).first()
                    if replacement:
                        if week[0] < replacement.end_date and week[1] > replacement.start_date:
                            new_row += [('replacementText',
                                         f'ЗАМЕНА;{replacement.grade};'
                                         f'{replacement.topic};{replacement.cabinet};')]
                    else:
                        new_row += [
                            f'{lessons_iter[0].grade};{lessons_iter[0].topic};'
                            f'{lessons_iter[0].cabinet}']
                else:
                    new_row += ['-']
            rows.append(new_row)
    return header, rows


def dateTime_html_format(datetime_data):
    months_eng_to_rus = {
        'Jan': 'Янв',
        'Feb': 'Фев',
        'Mar': 'Мар',
        'Apr': 'Апр',
        'May': 'Май',
        'Jul': 'Июл',
        'Aug': 'Авг',
        'Sep': 'Сен',
        'Oct': 'Окт',
        'Nov': 'Ноя',
        'Dec': 'Дек'
    }
    return datetime_data.strftime('%d.%m %H:%M')


@app.route('/statistic', methods=['POST', 'GET'])
def show_statistic():
    """show statistics"""
    interval = 'day'
    replacements = {"replace": 0, "replaced": 0}

    if request.method == 'POST':
        interval = request.form['interval']
    now = datetime.datetime.now()
    try:
        if interval == 'day':
            date = now.day
        elif interval == 'week':
            mon = now.day - now.weekday()
            sun = mon + 6
            date = range(mon, sun + 1)
        else:
            date = [now.month]

        param = analyze.analyze(date, current_user.grade,
                                current_user.access_level, current_user.id)
    except ValueError:
        return render_template('statistic.html', title="Статистика", interval=interval,
                               error="Уроков нет на данном промежутке")

    GoogleCharts.pie_chart(param)
    GoogleCharts.combo_chart(param)
    try:
        if current_user.access_level == 3:
            GoogleCharts.bar_chart(param)
        elif current_user.access_level == 2:
            replacements = GoogleCharts.area_chart(param)
    except ValueError:
        return render_template('statistic.html', title="Статистика", interval=interval,
                               error_rep="Замен нет на данном промежутке нет", error=None)
    return render_template('statistic.html', title="Статистика", interval=interval,
                           error=None, error_rep=None, replacements=replacements, **param)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/token', methods=['GET', 'POST'])
def token_check():
    """check token"""
    form = TokenForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.token == form.token.data).first()
        if user:
            if user.email is None:
                return redirect(f"/register/{form.token.data}")
            return redirect(f"/login/{form.token.data}")
        return render_template('token_check.html',
                               message="Неправильный токен",
                               form=form)
    return render_template('token_check.html', title='Авторизация', form=form)


@app.route('/login/<string:token>', methods=['GET', 'POST'])
def login(token):
    """user login"""
    form = LoginForm()
    form.token.data = token
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data,
                                          User.token == form.token.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        user = db_sess.query(User).filter(User.token == form.token.data).first()
        if user:
            return render_template('login.html',
                                   message="Неправильный логин или пароль",
                                   form=form)
        return render_template('login.html',
                               message="Несуществующий токен",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/register/<string:token>', methods=['GET', 'POST'])
def register(token):
    """register user"""
    db_sess = db_session.create_session()
    form = RegisterForm()
    if request.method == "GET":
        user = db_sess.query(User).filter(User.token == token).first()
        if not user:
            return render_template('register.html', title='Регистрация',
                                   message="Несуществующий токен",
                                   form=form)
        form.token.data = user.token
        form.grade.data = user.grade
        form.access_level.choices = [(user.access_level, user.access_level)]
        form.surname.data = user.surname
        form.name.data = user.name
        form.patronymic.data = user.patronymic
        image_path = user.image
        print(image_path)
    if form.validate_on_submit():
        if db_sess.query(User).filter(User.token == form.token.data).first().email is not None:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Этот пользователь уже зарегистрирован")
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = db_sess.query(User).filter(User.token == form.token.data).first()
        user_elem = db_sess.query(User).filter(User.id == user.id).first()
        user_elem.name = form.name.data
        user_elem.surname = form.surname.data
        user_elem.patronymic = form.patronymic.data
        user_elem.email = form.email.data
        user_elem.set_password(form.password.data)

        # пикча
        file = request.files['file']
        if file:
            file.save('static/img/' + secure_filename(file.filename))

            fixed_width = 200
            img = PIL.Image.open('static/img/' + secure_filename(file.filename))
            width_percent = (fixed_width / float(img.size[0]))
            height_size = int((float(img.size[0]) * float(width_percent)))
            new_image = img.resize((fixed_width, height_size))
            new_image.save('static/img/' + secure_filename(file.filename))

            us.image = 'static/img/' + secure_filename(file.filename)

        db_sess.commit()
        return redirect(f'/login/{user.token}')
    return render_template('register.html', title='Регистрация', form=form,
                           image_path=image_path)


@app.route('/user_edit/<int:id>', methods=['GET', 'POST'])
@login_required
def user_edit(id):
    """edit user data"""
    form = RegisterForm()
    level = 0
    if request.method == "GET":
        db_sess = db_session.create_session()
        if current_user.id == 1:
            user = db_sess.query(User).filter(User.id == id).first()
            form.access_level.choices = [(3, 3), (2, 2), (1, 1)]
            form.access_level.data = user.access_level
            level = 1 if user.id != 1 else 0
            form.password.validators = []
            form.password_again.validators = []
        else:
            user = db_sess.query(User).filter(User.id == current_user.id).first()
            form.access_level.choices = [user.access_level]
            level = 0

        if user:
            form.name.data = user.name
            form.surname.data = user.surname
            form.patronymic.data = user.patronymic
            form.grade.data = user.grade
            form.email.data = user.email
            form.token.data = user.token
        else:
            abort(404)
        image_path = user.image

    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Редактирование профиля',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data,
                                      User.token != form.token.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        if current_user.id == 1:
            user = db_sess.query(User).filter(User.id == id).first()
            user.access_level = form.access_level.data
        else:
            user = db_sess.query(User).filter(User.id == current_user.id).first()

        if user:
            user.name = form.name.data
            user.surname = form.surname.data
            user.patronymic = form.patronymic.data
            user.grade = form.grade.data
            user.email = form.email.data
            user.token = form.token.data
            user.set_password(form.password.data)

            # пикча
            file = request.files['file']
            if file:
                file.save('static/img/' + secure_filename(file.filename))

                fixed_width = 200
                img = PIL.Image.open('static/img/' + secure_filename(file.filename))
                width_percent = (fixed_width / float(img.size[0]))
                height_size = int((float(img.size[0]) * float(width_percent)))
                new_image = img.resize((fixed_width, height_size))
                new_image.save('static/img/' + secure_filename(file.filename))

                if user.image.split('/')[-1] != 'default.png':
                    os.remove(user.image[1:])
                user.image = '/static/img/' + secure_filename(file.filename)
            db_sess.commit()
            return redirect('/')
        abort(404)
    return render_template('register.html', title='Редактирование профиля', form=form,
                           level=level,
                           image_path=image_path)


app.run()
