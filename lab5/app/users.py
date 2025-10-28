from flask import Blueprint, request, render_template, url_for, flash, redirect
from flask_login import login_required
import re
import mysql.connector as connector
from .utils.decorators import check_rights

from .repositories.user_repository import UserRepository
from .repositories.role_repository import RoleRepository
from .dbConnector import db

user_repository = UserRepository(db)
role_repository = RoleRepository(db)

bp = Blueprint('users', __name__, url_prefix='/users')


def validate_password(password, new_password = ''):
    def is_empty(val): return val is None or val.strip() == ''

    if new_password and new_password != password:
        return (False, 'Пароли не совпадают.')
    if is_empty(password):
        return (False, 'Поле не может быть пустым')
    elif len(password) < 8 or len(password) > 128:
        return (False, 'Пароль должен быть от 8 до 128 символов')
    elif not re.search(r'[A-ZА-Я]', password) or not re.search(r'[a-zа-я]', password):
        return (False, 'Пароль должен содержать как минимум одну заглавную и одну строчную букву')
    elif not re.search(r'\d', password):
        return (False, 'Пароль должен содержать хотя бы одну цифру')
    elif re.search(r'\s', password):
        return (False, 'Пароль не должен содержать пробелы')
    elif not re.fullmatch(r'[A-Za-zА-Яа-яЁё0-9~!?@#$%^&*_\-+()\[\]{}><\/\\|"\'.:,;]+', password):
        return (False, 'Пароль содержит недопустимые символы')
    return (True,)

def validate_username(username):
    def is_empty(val): return val is None or val.strip() == ''
    if is_empty(username):
        return (False, 'Поле не может быть пустым')
    elif not re.fullmatch(r'[A-Za-z0-9]{5,}', username):
        return (False, 'Логин должен содержать не менее 5 латинских букв и/или цифр')
    return (True,)



def validate_user_data(data, require_username=True, require_password=True):
    errors = {}

    def is_empty(val): return val is None or val.strip() == ''

    # Логин
    if require_username:
        username = data.get('username', '')
        print(validate_username(username))
        validate_username_result = validate_username(username)
        if validate_username_result[0] == False:
            errors['username'] = validate_username_result[1]

    # Пароль
    if require_password:
        password = data.get('password', '')
        validate_password_result = validate_password(password)
        if validate_password_result[0] == False:
            errors['password'] = validate_password_result[1]


    # Обязательные поля
    if is_empty(data.get('first_name')):
        errors['first_name'] = 'Поле не может быть пустым'
    if is_empty(data.get('last_name')):
        errors['last_name'] = 'Поле не может быть пустым'

    return errors
@bp.route('/')
def index():
    return render_template('users/index.html', users=user_repository.all())


@bp.route('/<int:user_id>')
@login_required
@check_rights('view_user')
def show(user_id):
    user = user_repository.get_by_id(user_id)
    if user is None:
        flash('Пользователя нет в базе данных', 'danger')
        return redirect(url_for('users.index'))
    user_role = role_repository.get_by_id(user.role_id)
    return render_template('users/show.html', user_data=user, user_role=getattr(user_role, 'name', ''))


@bp.route('/new', methods=['POST', 'GET'])
@login_required
@check_rights('create_user')
def new():
    user_data = {}
    form_errors = {}

    if request.method == 'POST':
        fields = ("username", 'password', 'first_name', 'middle_name', 'last_name', 'role_id')
        user_data = {field: request.form.get(field) or None for field in fields}

        role_id = request.form.get('role_id')  # Получаем role_id из формы
        if role_id:
            user_data['role_id'] = role_id  # Устанавливаем role_id

        form_errors = validate_user_data(user_data)

        if not form_errors:
            try:
                user_repository.create(**user_data)
                flash('Учётная запись создана', 'success')
                return redirect(url_for('users.index'))
            except Exception as e:
                flash('Ошибка при создании пользователя', 'danger')
                db.connect().rollback()

    return render_template('users/new.html',
                           user_data=user_data,
                           roles=role_repository.all(),
                           form_errors=form_errors)


@bp.route('/<int:user_id>/edit', methods=['POST', 'GET'])
@login_required
@check_rights('edit_user')
def edit(user_id):
    user = user_repository.get_by_id(user_id)
    if user is None:
        flash('Пользователя нет в базе данных', 'danger')
        return redirect(url_for('users.index'))

    user_data = user
    form_errors = {}

    if request.method == 'POST':
        fields = ('first_name', 'middle_name', 'last_name', 'role_id')
        user_data = {field: request.form.get(field) or None for field in fields}
        user_data['user_id'] = user_id

        form_errors = validate_user_data(user_data, require_username=False, require_password=False)

        if not form_errors:
            try:
                user_repository.update(**user_data)
                flash('Учётная запись успешно изменена', 'success')
                return redirect(url_for('users.index'))
            except Exception as e:
                flash('Произошла ошибка при изменении данных.', 'danger')
                db.connect().rollback()

    return render_template('users/edit.html',
                           user_data=user_data,
                           roles=role_repository.all(),
                           form_errors=form_errors)


@bp.route('/<int:user_id>/delete', methods=['POST'])
@login_required
@check_rights('delete_user')
def delete(user_id):
    user_repository.delete(user_id)
    flash('Учётная запись успешно удалена', 'success')
    return redirect(url_for('users.index'))
