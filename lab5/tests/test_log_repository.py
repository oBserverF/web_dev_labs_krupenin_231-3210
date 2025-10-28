import pytest
from collections import namedtuple


@pytest.mark.usefixtures("clear_visit_logs")
def test_get_all_with_users(user_repository, log_repository, example_users):
    # Добавим записи в таблицу visit_logs
    logs_data = [
        (1, example_users[0].id, '/home', '2025-05-10 10:00:00'),
        (2, example_users[1].id, '/about', '2025-05-10 11:00:00'),
        (3, example_users[0].id, '/home', '2025-05-10 12:00:00'),
    ]
    
    connection = user_repository.db_connector.connect()
    with connection.cursor() as cursor:
        query = "INSERT INTO visit_logs (id, user_id, path, created_at) VALUES (%s, %s, %s, %s)"
        cursor.executemany(query, logs_data)
        connection.commit()

    # Получаем логи для user_id = 1
    logs = log_repository.get_all_with_users(user_id=example_users[0].id, is_admin=False)

    assert len(logs) == 2
    assert logs[0].user_name == "Smith John Doe"
    assert logs[0].path == '/home'
    
    # Получаем логи для администратора (должен видеть все логи)
    logs_admin = log_repository.get_all_with_users(user_id=None, is_admin=True)

    assert len(logs_admin) == 3
    assert logs_admin[1].user_name == "Johnson Jane Doe"
    assert logs_admin[1].path == '/about'


@pytest.mark.usefixtures("clear_visit_logs")
def test_count_all(log_repository, example_users):
    # Добавим записи в таблицу visit_logs
    logs_data = [
        (1, example_users[0].id, '/home', '2025-05-10 10:00:00'),
        (2, example_users[1].id, '/about', '2025-05-10 11:00:00'),
        (3, example_users[0].id, '/home', '2025-05-10 12:00:00'),
    ]
    
    connection = log_repository.db_connector.connect()
    with connection.cursor() as cursor:
        query = "INSERT INTO visit_logs (id, user_id, path, created_at) VALUES (%s, %s, %s, %s)"
        cursor.executemany(query, logs_data)
        connection.commit()

    # Получаем количество логов
    total_logs = log_repository.count_all(user_id=None, is_admin=True)
    assert total_logs == 3

    # Для обычного пользователя должно быть 2 лога
    total_logs_user = log_repository.count_all(user_id=example_users[0].id, is_admin=False)
    assert total_logs_user == 2


@pytest.mark.usefixtures("clear_visit_logs")
def test_get_by_page(log_repository, example_users):
    # Добавим записи в таблицу visit_logs
    logs_data = [
        (1, example_users[0].id, '/home', '2025-05-10 10:00:00'),
        (2, example_users[1].id, '/about', '2025-05-10 11:00:00'),
        (3, example_users[0].id, '/home', '2025-05-10 12:00:00'),
        (4, example_users[1].id, '/contact', '2025-05-10 13:00:00'),
        (5, example_users[0].id, '/home', '2025-05-10 14:00:00'),
    ]
    
    connection = log_repository.db_connector.connect()
    with connection.cursor() as cursor:
        query = "INSERT INTO visit_logs (id, user_id, path, created_at) VALUES (%s, %s, %s, %s)"
        cursor.executemany(query, logs_data)
        connection.commit()

    # Получаем логи, группируя по пути
    logs_by_page = log_repository.get_by_page(user_id=None, is_admin=True)

    assert len(logs_by_page) == 3
    assert logs_by_page[0].path == '/home'
    assert logs_by_page[0].visits == 3

@pytest.mark.usefixtures("clear_visit_logs")
def test_get_by_users(log_repository, example_users):
    # Добавим записи в таблицу visit_logs
    logs_data = [
        (1, example_users[0].id, '/home', '2025-05-10 10:00:00'),
        (2, example_users[1].id, '/about', '2025-05-10 11:00:00'),
        (3, example_users[0].id, '/home', '2025-05-10 12:00:00'),
        (4, example_users[1].id, '/contact', '2025-05-10 13:00:00'),
        (5, example_users[0].id, '/home', '2025-05-10 14:00:00'),
    ]
    
    connection = log_repository.db_connector.connect()
    with connection.cursor() as cursor:
        query = "INSERT INTO visit_logs (id, user_id, path, created_at) VALUES (%s, %s, %s, %s)"
        cursor.executemany(query, logs_data)
        connection.commit()

    # Получаем логи по пользователям
    logs_by_users = log_repository.get_by_users()

    assert len(logs_by_users) == 2
    assert logs_by_users[0].first_name == 'John'
    assert logs_by_users[0].last_name == 'Smith'
    assert logs_by_users[0].visits == 3

