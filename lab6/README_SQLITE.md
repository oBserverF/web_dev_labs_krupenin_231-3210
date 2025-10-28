# Lab6: SQLite Setup and Data Fill

## Быстрый запуск с SQLite

1. Убедитесь, что в `lab6/app/config.py` используется:
   ```python
   SQLALCHEMY_DATABASE_URI = 'sqlite:///lab6.db'
   ```
2. Инициализируйте базу данных:
   ```bash
   cd lab6
   export FLASK_APP=app:create_app
   flask db init
   flask db migrate -m "Initial migration"
   flask db upgrade
   ```
3. Заполните базу данных из скрипта:
   ```bash
   python fill_db.py
   ```
   После этого база `lab6.db` будет содержать тестовые данные.

## Деплой на PythonAnywhere

- Просто скопируйте/запушьте файлы проекта.
- Убедитесь, что в WSGI-файле не используются переменные для MySQL.
- После деплоя выполните команды выше в консоли PA.
- Для сброса данных — удалите файл `lab6.db` и повторите шаги.

## Важно
- SQLite работает на бесплатном аккаунте PA без ограничений.
- Все данные хранятся в файле `lab6.db` в папке lab6.
- Скрипт `fill_db.py` можно запускать повторно для наполнения.
