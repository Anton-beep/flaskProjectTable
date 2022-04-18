"""main"""

import os
import secrets
import datetime
import time

from PIL import Image

from flask import Flask, redirect, render_template, request, send_file
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from flask_restful import abort, Api
from sqlalchemy import and_
from werkzeug.utils import secure_filename
import xlsxwriter

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

from data.get_table_data_from_db import *
from data.edit_db_from_base import *

app = Flask(__name__)
app.config['SECRET_KEY'] = 'Church_Of_Saint_Floppa'
db_session.global_init("db/timetable.db")

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

post_hnd = datetime.datetime.now()


@app.route('/', methods=['POST', 'GET'])
def base():
    """view table"""
    global NOW_DAY, TABLE_WEEK, post_hnd
    rows = []
    header = []
    form = None
    form_replacement = None

    if current_user.is_authenticated:
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.id == current_user.id).first()
        form = EditLessonForm()
        if form.validate_on_submit() and user.access_level == 3 and form.title.data != 'notPOST':
            data = request.form
            if data and (datetime.datetime.now() - post_hnd).seconds > 1:
                if data['title'] == 'Изменение/Создание замены':
                    # replacement
                    edit_write_replacement(data, form, TABLE_WEEK)
                else:
                    # lesson
                    edit_write_lesson(data, form)
        elif request.method == 'POST':
            data = request.json
            if data['message'] == 'new week':
                NOW_DAY = datetime.datetime.strptime(data['day'], '%Y-%m-%d')
                TABLE_WEEK = get_week_from_day(NOW_DAY)
                NOW_DAY = NOW_DAY.strftime('%Y-%m-%d')
            else:
                if user.access_level == 3:
                    if data['message'] == 'delete lesson':
                        teacher = db_sess.query(User).filter(
                            User.name == data['teacher'].split()[1],
                            User.surname == data['teacher'].split()[0]).first()
                        time_db = convert_table_text_to_time(data['time'])
                        lesson_to_del = db_sess.query(Lesson).filter(
                            and_(Lesson.time == time_db, Lesson.teacher == teacher.id)).first()
                        if lesson_to_del:
                            db_sess.delete(lesson_to_del)
                            db_sess.commit()
                    elif data['message'] == 'delete replacement':
                        teacher = db_sess.query(User).filter(
                            User.name == data['teacher'].split()[1],
                            User.surname == data['teacher'].split()[0]).first()
                        time_db = convert_table_text_to_time(data['time'])
                        lessons_time = list(db_sess.query(Lesson).filter(Lesson.time == time_db))

                        for lesson in lessons_time:
                            rep_to_del = db_sess.query(Replacement).filter(
                                and_(Replacement.lesson == lesson.id,
                                     Replacement.teacher == teacher.id)).first()
                            if rep_to_del:
                                db_sess.delete(rep_to_del)
                                db_sess.commit()
                                break

            post_hnd = datetime.datetime.now()

        if user.access_level == 1:
            header, rows = table_data_for_user(user.grade, TABLE_WEEK)
        elif user.access_level == 2:
            header, rows = table_data_for_teacher(user.id, TABLE_WEEK)
        elif user.access_level == 3:
            header, rows = table_data_for_admin(TABLE_WEEK)

    return render_template("show_table.html", rows=rows, header=header, form=form,
                           form_replacement=form_replacement, now_day=NOW_DAY)


@app.route('/users', methods=['POST', 'GET'])
def users():
    """lists all users"""
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
    all_users = list(db_sess.query(User))
    rows = []
    for user in all_users:
        row = [user.id, user.name, user.surname, user.patronymic, user.grade, user.email,
               user.access_level, user.token]
        row = ['-' if el is None else el for el in row]
        rows.append(row)

    return header, rows


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


def get_week_from_day(day):
    """get week from day DateTime"""
    week_num = day.weekday()
    start_week_day = day - datetime.timedelta(days=week_num)
    end_week_day = start_week_day + datetime.timedelta(days=6)
    print(start_week_day, end_week_day)
    return start_week_day, end_week_day


NOW_DAY = datetime.datetime.today().strftime('%Y-%m-%d')
TABLE_WEEK = get_week_from_day(
    datetime.datetime.today().replace(hour=0, minute=0, second=0, microsecond=0))


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
                    grade_users = list(db_sess.query(User).filter(User.grade == form.grade.data))
                    set_users = set(grade_users) & set_users
                if form.surname.data:
                    surname_users = list(db_sess.query(User).filter(
                        User.surname == form.surname.data))
                    set_users = set(surname_users) & set_users
                if form.name.data:
                    name_users = list(db_sess.query(User).filter(User.name == form.name.data))
                    set_users = set(name_users) & set_users
                if form.patronymic.data:
                    patronymic_users = list(db_sess.query(User).filter(
                        User.patronymic == form.patronymic.data))
                    set_users = set(patronymic_users) & set_users
                if len(set_users) > 0:
                    message = 'Такой пользователь уже есть'
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
            header, rows = table_data_for_user(user.grade, TABLE_WEEK)
        elif user.access_level == 2:
            header, rows = table_data_for_teacher(user.id, TABLE_WEEK)
        elif user.access_level == 3:
            header, rows = table_data_for_admin(TABLE_WEEK)
        else:
            header = None
            rows = None

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
    abort(404)


def style_excel(val):
    """style excel"""
    style = """"""
    if 'ЗАМЕНА' in val.split():
        style += ' background-color: orange;'
    return style


def date_time_html_format(datetime_data):
    """convert to short DateTime"""
    return datetime_data.strftime('%d.%m %H:%M')


@app.route('/statistic', methods=['POST', 'GET'])
def show_statistic():
    """show statistics"""
    interval = 'day'
    replacements = {"replace": 0, "replaced": 0}

    if request.method == 'POST':
        interval = request.form['interval']

    try:
        param = analyze.analyze(interval, current_user.grade,
                                current_user.access_level, current_user.id)
    except Exception as er:
        print(er)
        return render_template('statistic.html', title="Статистика", interval=interval,
                               error="Уроков нет на данном промежутке")

    GoogleCharts.pie_chart(param)
    GoogleCharts.combo_chart(param)
    try:
        if current_user.access_level == 3:
            GoogleCharts.bar_chart(param)
        elif current_user.access_level == 2:
            replacements = GoogleCharts.area_chart(param)
    except Exception:
        return render_template('statistic.html', title="Статистика", interval=interval,
                               error_rep="Замен нет на данном промежутке нет", error=None)
    return render_template('statistic.html', title="Статистика", interval=interval,
                           error=None, error_rep=None, replacements=replacements, **param)


@login_manager.user_loader
def load_user(user_id):
    """load user"""
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/logout')
@login_required
def logout():
    """logout user"""
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
            if user.hashed_password is None:
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
            img = Image.open('static/img/' + secure_filename(file.filename))
            width_percent = (fixed_width / float(img.size[0]))
            height_size = int((float(img.size[0]) * float(width_percent)))
            new_image = img.resize((fixed_width, height_size))
            new_image.save('static/img/' + secure_filename(file.filename))

            user_elem.image = 'static/img/' + secure_filename(file.filename)

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
                img = Image.open('static/img/' + secure_filename(file.filename))
                width_percent = (fixed_width / float(img.size[0]))
                height_size = int((float(img.size[0]) * float(width_percent)))
                new_image = img.resize((fixed_width, height_size))
                new_image.save('static/img/' + secure_filename(file.filename))

                if user.image.split('/')[-1] != 'default.png':
                    try:
                        os.remove(user.image[1:])
                    except FileNotFoundError:
                        # по какой-то причине, старой пикчи нет
                        pass
                user.image = '/static/img/' + secure_filename(file.filename)
            db_sess.commit()
            return redirect('/')
        abort(404)
    return render_template('register.html', title='Редактирование профиля', form=form,
                           level=level,
                           image_path=image_path)


app.run()
