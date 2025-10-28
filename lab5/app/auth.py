from functools import wraps
from flask import Blueprint, request, render_template, url_for, flash, redirect
from flask_login import LoginManager, UserMixin, current_user, login_user, logout_user, login_required
from .repositories.user_repository import UserRepository
from .repositories.role_repository import RoleRepository
from .dbConnector import db
from .users import validate_password
import re

user_repository = UserRepository(db)
role_repository = RoleRepository(db)

bp = Blueprint('auth', __name__, url_prefix='/auth')

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Для доступа к запрашиваемой странице необходимо пройти процедуру аутенфикации'
login_manager.login_message_category = 'warning'

class User(UserMixin):
    def __init__(self, user_id, username, role_name=None):
        self.id = user_id
        self.user_login = username
        self.role = role_name
        
@login_manager.user_loader
def load_user(user_id):
    user = user_repository.get_by_id(user_id)
    if user is not None:
        role = role_repository.get_by_id(user.role_id) if user.role_id else None
        return User(user.id, user.username, role.name if role else None)
    return None

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember_me = request.form.get('remember_me') == 'on'

        user = user_repository.get_by_username_and_password(username, password)

        if user is not None:
            flash('Вы успешно аутентифицированы', 'success')
            login_user(User(user.id, user.username), remember=remember_me)
            return redirect(request.args.get('next') if request.args.get('next') else url_for('users.index'))
        flash('Неверные данные для аутенфикации.', 'danger')
    return render_template('auth/login.html')

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('users.index'))


# Логика для смены пароля
@bp.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    form_errors = {}

    if request.method == 'POST':
        old_password = request.form['old_password']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']

        # Проверка старого пароля
        username = user_repository.get_by_id(current_user.id).username
        user = user_repository.get_by_username_and_password(username, old_password)
        if not user:
            form_errors['old_password'] = 'Неверный старый пароль.'

        # Проверка нового пароля
        validate_password_result = validate_password(new_password)
        if validate_password_result[0] == False:
            form_errors['new_password'] = validate_password_result[1]
        elif new_password != confirm_password:
            form_errors['confirm_password'] = 'Пароли не совпадают.'

        # Если ошибок нет, сохраняем новый пароль
        if not form_errors:
            # Обновляем пароль пользователя в базе
            user_repository.update_password(current_user.id, new_password)
            flash('Пароль успешно изменён!', 'success')
            return redirect(url_for('users.index'))

        flash('Произошла ошибка при изменении пароля.', 'danger')

    return render_template('auth/change_password.html', form_errors=form_errors)