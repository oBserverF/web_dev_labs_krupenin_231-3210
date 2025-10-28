from flask import render_template, request
from flask_login import login_required, current_user
from . import bp
from ..dbConnector import db
from ..repositories.log_repository import LogRepository
from ..repositories.user_repository import UserRepository

from ..utils.decorators import check_rights

import csv
from io import StringIO
from flask import Response

user_repository = UserRepository(db)

# @bp.route('/')
# @login_required
# def index():
#     repo = LogRepository(db)

#     # Определяем, администратор ли это
#     is_admin = user_repository.get_is_admin_by_id(current_user.id)

#     # Получаем логи: все для админа, только свои для обычных пользователей
#     logs = repo.get_all_with_users(user_id=current_user.id, is_admin=is_admin)
    
#     return render_template('logs/index.html', logs=logs)


@bp.route('/')
@login_required
def index():
    repo = LogRepository(db)
    user_repo = UserRepository(db)

    # Параметры пагинации
    page = int(request.args.get('page', 1))
    per_page = 20
    offset = (page - 1) * per_page

    is_admin = user_repo.get_is_admin_by_id(current_user.get_id())
    logs = repo.get_all_with_users(current_user.get_id(), is_admin, limit=per_page, offset=offset)
    total = repo.count_all(current_user.get_id(), is_admin)

    total_pages = (total + per_page - 1) // per_page

    user_role = user_repo.get_role_name(current_user.get_id())

    return render_template('logs/index.html', logs=logs, page=page, total_pages=total_pages, user_role = user_role)

@bp.route('/by_page')
@login_required
@check_rights('by_page_report')
def report_by_page():
    repo = LogRepository(db)
    
    page_reports = repo.get_by_page()
    return render_template('logs/report_by_page.html', page_reports=page_reports)

@bp.route('/by_user')
@login_required
@check_rights('by_user_report')
def report_by_user():
    repo = LogRepository(db)
    
    user_reports = repo.get_by_users()
    return render_template('logs/report_by_user.html', user_reports=user_reports)


@bp.route('/export/by_page')
@login_required
@check_rights('export_by_page_report')
def export_page_report():
    repo = LogRepository(db)
    data = repo.get_by_page()

    si = StringIO()
    writer = csv.writer(si)
    writer.writerow(['№', 'Страница', 'Количество посещений'])

    for i, row in enumerate(data, start=1):
        writer.writerow([i, row.path, row.visits])

    output = si.getvalue()
    return Response(output, mimetype='text/csv', headers={
        'Content-Disposition': 'attachment; filename=report_by_page.csv'
    })


@bp.route('/export/by_user')
@login_required
@check_rights('export_by_user_report')
def export_user_report():
    repo = LogRepository(db)
    data = repo.get_by_users()

    si = StringIO()
    writer = csv.writer(si)
    writer.writerow(['№', 'Пользователь', 'Количество посещений'])

    for i, row in enumerate(data, start=1):
        if row.first_name:
            name = f"{row.last_name} {row.first_name}"
        else:
            name = "Неаутентифицированный пользователь"
        writer.writerow([i, name, row.visits])

    output = si.getvalue()
    return Response(output, mimetype='text/csv', headers={
        'Content-Disposition': 'attachment; filename=report_by_user.csv'
    })
