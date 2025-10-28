from app.users import validate_password
from app.users import validate_username
import pytest

def test_get_by_id_with_existing_user(user_repository, example_users):
    user = user_repository.get_by_id(example_users[0].id)
    assert user.id == example_users[0].id
    assert user.username == example_users[0].username
    assert user.first_name == example_users[0].first_name


def test_get_by_id_with_nonexisting_user(user_repository):
    user = user_repository.get_by_id(9999)
    assert user is None


def test_get_by_username_and_password_with_valid_credentials(user_repository, example_users):
    user = user_repository.get_by_username_and_password('user1', 'password1')
    assert user.id == example_users[0].id
    assert user.username == example_users[0].username


def test_get_by_username_and_password_with_invalid_credentials(user_repository):
    user = user_repository.get_by_username_and_password('nonexistent_user', 'wrong_password')
    assert user is None


def test_all_with_nonempty_db(user_repository, example_users):
    users = user_repository.all()
    assert len(users) == len(example_users)
    for loaded_user, example_user in zip(users, example_users):
        assert loaded_user.id == example_user.id
        assert loaded_user.username == example_user.username


def test_create_user(user_repository, existing_role):
    user_repository.create('newuser', 'newpassword', 'Alice', 'B', 'C', existing_role.id)
    user = user_repository.get_by_username_and_password('newuser', 'newpassword')
    assert user is not None
    assert user.username == 'newuser'


def test_update_user(user_repository, example_users):
    user_repository.update(example_users[0].id, 'Updated', 'Name', 'Test', example_users[0].role_id)
    updated_user = user_repository.get_by_id(example_users[0].id)
    assert updated_user.first_name == 'Updated'
    assert updated_user.last_name == 'Test'


def test_delete_user(user_repository, example_users):
    user_repository.delete(example_users[0].id)
    user = user_repository.get_by_id(example_users[0].id)
    assert user is None


def test_update_password(user_repository, example_users):
    new_password = 'newpassword123'
    user_repository.update_password(example_users[0].id, new_password)
    user = user_repository.get_by_username_and_password(example_users[0].username, new_password)
    assert user is not None


@pytest.mark.parametrize("password,expected_error", [
    ("Short1", 'Пароль должен быть от 8 до 128 символов')
])
def test_short_password_validation(password, expected_error):
    validate_password_result = validate_password(password)
    assert validate_password_result[1] == expected_error


@pytest.mark.parametrize("password,expected_error", [
    ('A' * 129, 'Пароль должен быть от 8 до 128 символов')
])
def test_long_password_validation(password, expected_error):
    validate_password_result = validate_password(password)
    assert validate_password_result[1] == expected_error

@pytest.mark.parametrize("password,expected_error", [
    ('password123', 'Пароль должен содержать как минимум одну заглавную и одну строчную букву')
])
def test_password_missing_uppercase(password, expected_error):
    validate_password_result = validate_password(password)
    assert validate_password_result[1] == expected_error

@pytest.mark.parametrize("password,expected_error", [
    ('PASSWORD123', 'Пароль должен содержать как минимум одну заглавную и одну строчную букву')
])
def test_password_missing_lowercase(password, expected_error):
    validate_password_result = validate_password(password)
    assert validate_password_result[1] == expected_error

@pytest.mark.parametrize("password,expected_error", [
    ('PasswordNoDigit', 'Пароль должен содержать хотя бы одну цифру')
])
def test_password_missing_digit(password, expected_error):
    validate_password_result = validate_password(password)
    assert validate_password_result[1] == expected_error

@pytest.mark.parametrize("password,expected_error", [
    ('Password 123', 'Пароль не должен содержать пробелы')
])
def test_password_with_spaces(password,expected_error):
    validate_password_result = validate_password(password)
    assert validate_password_result[1] == expected_error

@pytest.mark.parametrize("password,new_password,expected_error", [
    ('password1','password123', 'Пароли не совпадают.')
])

def test_password_confirmation_mismatch(password,new_password,expected_error):
    validate_password_result = validate_password(password, new_password)
    assert validate_password_result[1] == expected_error

@pytest.mark.parametrize("username,expected_error", [
    ('', 'Поле не может быть пустым')
])
def test_empty_username(username,expected_error):
    validate_username_result = validate_username(username)
    assert validate_username_result[1] == expected_error

@pytest.mark.parametrize("username,expected_error", [
    ('123a', 'Логин должен содержать не менее 5 латинских букв и/или цифр')
])
def test_short_password(username,expected_error):
    validate_username_result = validate_username(username)
    assert validate_username_result[1] == expected_error