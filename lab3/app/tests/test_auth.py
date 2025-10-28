import pytest
from flask import session
from app import app
from flask_login import current_user

def test_index(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b'Lab3' in response.data

def test_counter(client):
    with client.session_transaction() as sess:
        sess['counter'] = 0
    
    response = client.get('/counter')
    assert response.status_code == 200
    assert 'Вы посетили эту страницу 1 раз!' in response.data.decode('utf-8')
    
    response = client.get('/counter')
    assert 'Вы посетили эту страницу 2 раз!' in response.data.decode('utf-8')

def test_login_success(client):
    response = client.post('/login', data={'username': 'user1', 'password': 'pass1'}, follow_redirects=True)
    assert response.status_code == 200
    assert 'Вы успешно аутентифицированы' in response.data.decode('utf-8')

def test_login_failure(client):
    response = client.post('/login', data={'username': 'user1', 'password': 'wrong'}, follow_redirects=True)
    assert response.status_code == 200
    assert 'Неверные данные для аутенфикации.' in response.data.decode('utf-8')

def test_secret_page_authenticated(client, auth):
    auth.login()
    response = client.get('/secret')
    assert response.status_code == 200
    assert b'Secret page' in response.data

def test_secret_page_unauthenticated(client):
    response = client.get('/secret', follow_redirects=True)
    assert response.status_code == 200
    assert 'Для доступа к запрашиваемой странице необходимо пройти процедуру аутенфикации' in response.data.decode('utf-8')

def test_redirect_after_failed_secret_access(client, auth):
    response = client.get('/secret', follow_redirects=True)
    assert response.status_code == 200
    assert 'Для доступа к запрашиваемой странице необходимо пройти процедуру аутенфикации' in response.data.decode('utf-8')
    
    auth.login()
    response = client.get('/secret')
    assert response.status_code == 200
    assert b'Secret page' in response.data

def test_logout(client, auth):
    auth.login()
    response = client.get('/logout', follow_redirects=True)
    assert response.status_code == 200
    assert not current_user.is_authenticated

def test_navbar_authenticated(client, auth):
    auth.login()
    response = client.get('/')
    assert 'Выйти' in response.data.decode('utf-8')
    assert 'Секрет(Очень секретно)' in response.data.decode('utf-8')

def test_navbar_unauthenticated(client):
    response = client.get('/')
    assert 'Войти' in response.data.decode('utf-8')
    assert 'Секрет(Очень секретно)' not in response.data.decode('utf-8')

def test_remember_me(client):
    response = client.post('/login', data={'username': 'user1', 'password': 'pass1', 'remember_me': 'on'}, follow_redirects=True)
    assert response.status_code == 200
    assert client.get_cookie('remember_token') is not None
    assert 'Вы успешно аутентифицированы' in response.data.decode('utf-8')

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test_secret'
    with app.test_client() as client:
        yield client

@pytest.fixture
def auth(client):
    class AuthActions:
        def login(self, username='user1', password='pass1'):
            return client.post('/login', data={'username': username, 'password': password}, follow_redirects=True)
        
        def logout(self):
            return client.get('/logout', follow_redirects=True)
    
    return AuthActions()