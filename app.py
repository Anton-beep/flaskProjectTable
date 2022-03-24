import datetime

from flask import Flask, redirect, render_template
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from flask_restful import abort

from data.sqlalchemy import db_session
from data.API_resources import users_resources
from data.API_resources import lessons_resources
from data.API_resources import replacements_resources
from data.models.users import User
from data.models.lessons import Lesson
from data.models.replacements import Replacement

from forms.login import LoginForm
from forms.register import RegisterForm
from forms.token_check import TokenForm

import init

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

login_manager = LoginManager()
login_manager.init_app(app)

db_session.global_init('db/timetable.db')

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


def main():
    init.clear(True)

    db_session.global_init("db/timetable.db")

    init.fill_table(admin=True, users=True, lessons=True, replacements=True)

    app.run()


@app.route('/')
def base():
    param = {}
    file = "show_user.html"
    if current_user.is_authenticated:
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.id == current_user.id).first()

        if user.access_level == 1:
            param = param_for_user()
            file = "show_user.html"
        elif user.access_level == 2:
            param = param_for_teacher()
            file = "show_teacher.html"
        elif user.access_level == 3:
            param = param_for_admin()
            file = "show_admin.html"
        print(param)
    return render_template(file, **param)


def param_for_user():
    db_sess = db_session.create_session()
    grade = db_sess.query(User).filter(User.id == current_user.id).first().grade
    title = grade
    lessons = []
    for item in db_sess.query(Lesson).filter(Lesson.grade == grade).all():
        lesson = item.to_dict()
        lesson['duration'] = (item.end_date - item.start_date).seconds // 60
        teacher = db_sess.query(User).filter(User.id == item.teacher).first()
        lesson['teacher'] = ' '.join([teacher.surname, teacher.name, teacher.patronymic])

        lessons.append(lesson)

    replacements = {}
    for item in db_sess.query(Replacement).filter(Replacement.grade == grade).all():
        replacement = item.to_dict()
        replacement['duration'] = (item.end_date - item.start_date).seconds // 60
        teacher = db_sess.query(User).filter(User.id == item.teacher).first()
        replacement['teacher'] = ' '.join([teacher.surname, teacher.name, teacher.patronymic])

        replacements[item.lesson] = replacement
    return {"lessons": lessons, "rep": replacements, "title": title}


def param_for_teacher():
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == current_user.id).first()
    title = ' '.join([user.surname, user.name, user.patronymic])
    list_of_id = []

    lessons = []
    for item in db_sess.query(Lesson).filter(Lesson.teacher == user.id).all():
        lesson = item.to_dict()
        lesson['duration'] = (item.end_date - item.start_date).seconds // 60
        list_of_id.append(item.id)

        lessons.append(lesson)

    replacements = []
    for item in db_sess.query(Replacement).filter(Replacement.teacher == user.id).all():
        replacement = item.to_dict()
        replacement['duration'] = (item.end_date - item.start_date).seconds // 60
        replacement['old_topic'] = db_sess.query(Lesson).filter(Lesson.id == item.lesson).first().topic

        replacements.append(replacement)

    replaced = {}
    for item in db_sess.query(Replacement).filter(Replacement.lesson.in_(list_of_id)).all():
        rep = item.to_dict()
        rep['duration'] = (item.end_date - item.start_date).seconds // 60
        teacher = db_sess.query(User).filter(User.id == item.teacher).first()
        rep['teacher'] = ' '.join([teacher.surname, teacher.name, teacher.patronymic])

        replaced[item.lesson] = rep

    return {"lessons": lessons, "rep": replacements, "title": title, "replaced": replaced}


def param_for_admin():
    title = 'всех учеников и учитилей'
    db_sess = db_session.create_session()
    lessons = []
    for lesson in db_sess.query(Lesson).all():
        les = lesson.to_dict()
        teacher = db_sess.query(User).filter(User.id == lesson.teacher).first()
        les["teacher_name"] = ' '.join([teacher.surname, teacher.name, teacher.patronymic])
        les["duration"] = (lesson.end_date - lesson.start_date).seconds // 60

        lessons.append(les)

    replacements = {}
    for rep in db_sess.query(Replacement).all():
        replacements[rep.lesson] = rep.to_dict()
        teacher = db_sess.query(User).filter(User.id == replacements[rep.lesson]["teacher"]).first()
        replacements[rep.lesson]["teacher_name"] = ' '.join([teacher.surname, teacher.name,
                                                             teacher.patronymic])
        replacements[rep.lesson]["duration"] = (rep.end_date - rep.start_date).seconds // 60

    return {"lessons": lessons, "rep": replacements, "title": title}


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
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.token == token).first()
    form = RegisterForm()
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
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = db_sess.query(User).filter(User.token == form.token.data).first()
        us = db_sess.query(User).filter(User.id == user.id).first()
        us.name, us.surname, us.patronymic = form.name.data, form.surname.data, form.patronymic.data
        us.email = form.email.data
        us.set_password(form.password.data)
        db_sess.commit()
        return redirect(f'/login/{user.token}')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/user_edit/<int:id>', methods=['GET', 'POST'])
@login_required
def user_edit(id):
    form = RegisterForm()
    level = 0
    if request.method == "GET":
        db_sess = db_session.create_session()
        if current_user.id == 1:
            user = db_sess.query(User).filter(User.id == id).first()
            form.access_level.choices = [(1, 1), (2, 2), (3, 3)]
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

    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Редактирование профиля',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
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
            db_sess.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template('register.html', title='Редактирование профиля', form=form, level=level)


if __name__ == '__main__':
    main()
