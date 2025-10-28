from functools import wraps
from flask import redirect, url_for, flash
from flask_login import current_user
from ..repositories.user_repository import UserRepository
from ..dbConnector import db

user_repo = UserRepository(db)

# def check_rights(role_name):
#     def decorator(func):
#         @wraps(func)
#         def wrapper(*args, **kwargs):
#             if not current_user.is_authenticated:
#                 flash("Вы не авторизованы", "danger")
#                 return redirect(url_for('auth.login'))

#             is_allowed = user_repo.has_role(current_user.get_id(), role_name)
#             if not is_allowed:
#                 flash("У вас недостаточно прав для доступа к данной странице.", "danger")
#                 return redirect(url_for('users.index'))
#             return func(*args, **kwargs)
#         return wrapper
#     return decorator


from functools import wraps
from flask import redirect, url_for, flash
from flask_login import current_user
from ..repositories.user_repository import UserRepository
from ..repositories.role_repository import RoleRepository
from ..dbConnector import db

user_repository = UserRepository(db)
role_repository = RoleRepository(db)

# Связываем роли с правами
ROLE_PERMISSIONS = {
    'admin': {
        'create_user',
        'edit_user',
        'view_user',
        'delete_user',
        'view_logs',
        "by_page_report",
        "by_user_report",
        "export_by_page_report",
        "export_by_user_report"
    },
    'user': {
        'edit_self',
        'view_self',
        'view_own_logs'
    }
}

def is_editing_self(args, kwargs):
    return (
        ('user_id' in kwargs and kwargs['user_id'] == current_user.id) or
        (args and args[0] == current_user.id)
    )

def check_rights(permission):
    def decorator(view):
        @wraps(view)
        def wrapped_view(*args, **kwargs):

            if not current_user.is_authenticated:
                flash("Необходимо войти в систему.", "warning")
                return redirect(url_for('auth.login'))

            user = user_repository.get_by_id(current_user.id)
            role = role_repository.get_by_id(user.role_id)


            if role is None:
                flash("Роль пользователя не найдена.", "danger")
                return redirect(url_for('users.index'))
        
            permissions = ROLE_PERMISSIONS.get(role.name, set())

            # Специальная проверка: если действие над собой
            if permission == 'edit_user' and 'edit_self' in permissions and is_editing_self(args, kwargs):
                return view(*args, **kwargs)

            if permission == 'view_user' and 'view_self' in permissions:
                if 'user_id' in kwargs and kwargs['user_id'] == current_user.id:
                    return view(*args, **kwargs)

            if permission not in permissions:
                flash("У вас недостаточно прав для доступа к данной странице.", "danger")
                return redirect(url_for('users.index'))
            return view(*args, **kwargs)
        return wrapped_view
    return decorator
