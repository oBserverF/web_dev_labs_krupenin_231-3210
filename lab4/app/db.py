from flask import g, current_app
import sqlite3

class DBConnector:
    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        self.app = app
        self.app.teardown_appcontext(self.disconnect)

    def connect(self):
        if 'db' not in g:
            db_path = current_app.config.get('SQLITE_DB_PATH', 'lab4.db')
            g.db = sqlite3.connect(db_path)
            g.db.row_factory = sqlite3.Row
        return g.db

    def disconnect(self, e=None):
        db = g.pop('db', None)
        if db is not None:
            db.close()