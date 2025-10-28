import pytest
from flask import url_for

def test_redirect_if_not_logged_in(client):
    # Попытка зайти на защищённую страницу без логина
    response = client.get('/users/1', follow_redirects=True)
    assert response.status_code == 200
    assert response.request.path == '/auth/login'
    # Проверяем, что в ответе есть сообщение о необходимости входа
    assert 'Для доступа к запрашиваемой странице необходимо пройти процедуру аутенфикации' in response.data.decode('utf-8')

def test_redirect_if_no_rights(logged_in_user_without_rights, client):
    # Пользователь залогинен, но не имеет прав
    response = client.get('/users/1', follow_redirects=True)
    assert response.status_code == 200
    assert response.request.path == '/users/'
    # Проверяем, что есть сообщение о недостатке прав
    # print('##################################################')
    # print(response.data.decode('utf-8'))
    # print('##################################################')
    assert 'У вас недостаточно прав для доступа к данной странице.' in response.data.decode('utf-8')


@pytest.mark.usefixtures("clear_visit_logs")
def test_logging_of_visits(client, user_repository, example_users):
    with client:
        # Логинимся
        client.post('/auth/login', data={'username': example_users[0].username, 'password': 'password1'}, follow_redirects=True)
        
        # Очистим логи после логина, чтобы проверить только посещение /users/
        conn = user_repository.db_connector.connect()
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM visit_logs;")
            conn.commit()

        # Запрашиваем страницу /users/
        response = client.get(url_for('users.index'), follow_redirects=True)
        assert response.status_code == 200

        # Проверяем последний лог посещения
        with conn.cursor() as cursor:
            cursor.execute("SELECT path, user_id FROM visit_logs ORDER BY created_at DESC LIMIT 1")
            log = cursor.fetchone()
            assert log is not None
            assert log[0] == url_for('users.index')
            assert log[1] == example_users[0].id

def test_logs_pagination_correct_number(client, fifty_visit_logs):
    # Страница 1 — должно быть ровно 20 записей
    response = client.get('/logs?page=1', follow_redirects=True)
    assert response.status_code == 200
    html = response.data.decode('utf-8')
    assert html.count('<tr>') - 1 == 20

    # Страница 2 — тоже 20
    response = client.get('/logs?page=2', follow_redirects=True)
    assert response.status_code == 200
    html = response.data.decode('utf-8')
    assert html.count('<tr>') - 1 == 20

    # Страница 3 — остаток: от 1 до 20 записей
    response = client.get('/logs?page=3', follow_redirects=True)
    assert response.status_code == 200
    html = response.data.decode('utf-8')
    rows_count = html.count('<tr>') - 1

    assert 1 <= rows_count <= 20


def test_logs_pagination_out_of_range_page(client, fifty_visit_logs):
    # Запрос несуществующей страницы (например, 100)
    response = client.get('/logs?page=100', follow_redirects=True)
    assert response.status_code == 200
    html = response.data.decode('utf-8')
    # В таблице не должно быть записей
    assert html.count('<tr>') - 1 == 0
