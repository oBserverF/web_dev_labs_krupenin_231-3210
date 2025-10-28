import os

from flask import Flask, session, request
from flask_login import current_user
from .dbConnector import db

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_pyfile('config.py', silent=False)

    if test_config:
        app.config.from_mapping(test_config)
    
    db.init_app(app)

    from .cli import init_db_command
    app.cli.add_command(init_db_command)

    from . import auth
    app.register_blueprint(auth.bp)
    auth.login_manager.init_app(app)

    from . import users
    app.register_blueprint(users.bp)
    app.route('/', endpoint='index')(users.index)

    from . import logs
    app.register_blueprint(logs.bp)

    # --- Логирование посещений ---
    @app.before_request
    def log_visit():
        if request.path.startswith('/static') or request.path == '/favicon.ico':
            return

        conn = db.connect()
        cursor = conn.cursor()

        user_id = current_user.get_id()  if current_user.is_authenticated else None # None, если неаутентифицирован
        path = request.path

        try:
            cursor.execute(
                "INSERT INTO visit_logs (path, user_id) VALUES (%s, %s)",
                (path, user_id)
            )
            conn.commit()
        except Exception as e:
            conn.rollback()
            print(f"[log_visit] Ошибка логирования: {e}")
        finally:
            cursor.close()

    return app