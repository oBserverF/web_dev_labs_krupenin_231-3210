def test_args_template_one_arg(client, captured_templates):
    with captured_templates as templates:
        response = client.get("/args?name=Vladimir")
        assert response.status_code == 200

        assert len(templates) == 1
        template, context = templates[0]
        assert template.name == "args.html"

        assert "request" in context
        assert context["request"].args["name"] == "Vladimir"

        assert b"Vladimir" in response.data

def test_args_template_many_args(client, captured_templates):
    with captured_templates as templates:
        response = client.get("/args?name=Vladimir&age=20")
        assert response.status_code == 200

        assert len(templates) == 1
        template, context = templates[0]
        assert template.name == "args.html"

        assert "request" in context
        assert context["request"].args["name"] == "Vladimir"
        assert context["request"].args["age"] == "20"

        assert b"Vladimir" in response.data
        assert b"20" in response.data

def test_headers_template(client, captured_templates):
    with captured_templates as templates:
        response = client.get("/headers", headers={"Test-Header": "HeaderValue"})
        
        assert response.status_code == 200
        assert len(templates) == 1
        
        template, context = templates[0]
        assert template.name == "headers.html"

        assert "request" in context
        assert "Test-Header" in context["request"].headers
        assert context["request"].headers["Test-Header"] == "HeaderValue"

        assert b"Test-Header" in response.data
        assert b"HeaderValue" in response.data

def test_cookies(client):
    response = client.get("/cookies")
    assert response.status_code == 200
    assert response.headers["Set-Cookie"].startswith("bestProgrammer=VladimirK")

    response = client.get("/cookies")
    assert response.status_code == 200
    assert "Set-Cookie" in response.headers
    assert "bestProgrammer=;" in response.headers["Set-Cookie"]

def test_form(client):
    response = client.post('/form', data={'name': 'Vladimir', 'text': 'Hello, its a my krutoi test!'})
    
    assert response.status_code == 200
    
    assert b"Vladimir" in response.data
    assert b"Hello, its a my krutoi test!" in response.data


def test_valid_phone_number_1(client):
    response = client.post('/phone_form', data={'phone': '+7 (800) 555-35-35'})
    assert b"8-800-555-35-35" in response.data
    
def test_valid_phone_number_2(client):
    response = client.post('/phone_form', data={'phone': '7(800)5553535'})
    assert b"8-800-555-35-35" in response.data

def test_valid_phone_number_3(client):    
    response = client.post('/phone_form', data={'phone': '123.456.75.90'})
    assert b"8-123-456-75-90" in response.data

def test_invalid_phone_number_digit_count_less(client):
    response = client.post('/phone_form', data={'phone': '8800555353'})
    assert "Неверное количество цифр" in response.data.decode('utf-8')
    assert 'is-invalid' in response.data.decode('utf-8')  # Проверяем, что классы bootstrap применяются

def test_invalid_phone_number_digit_count_more(client):
    response = client.post('/phone_form', data={'phone': '880055535353'})
    assert "Неверное количество цифр" in response.data.decode('utf-8')
    assert 'is-invalid' in response.data.decode('utf-8')  # Проверяем, что классы bootstrap применяются

def test_invalid_phone_number_wrong_prefix(client):
    response = client.post('/phone_form', data={'phone': '5(800)5553535'})
    assert "Недопустимый ввод. Неверное количество цифр" in response.data.decode('utf-8')
    assert 'is-invalid' in response.data.decode('utf-8')

def test_invalid_phone_number_invalid_chars(client):
    response = client.post('/phone_form', data={'phone': '7(800)555A35-35'})
    assert "В номере телефона встречаются недопустимые символы" in response.data.decode('utf-8')
    assert 'is-invalid' in response.data.decode('utf-8') # Проверяем, что классы bootstrap применяются

def test_empty_phone_number(client):
    response = client.post('/phone_form', data={'phone': ''})
    assert "Неверное количество цифр" in response.data.decode('utf-8')
    assert 'is-invalid' in response.data.decode('utf-8')

def test_phone_field_invalid_class(client):
    response = client.post('/phone_form', data={'phone': '7800555353'})
    assert 'is-invalid' in response.data.decode('utf-8')  # Проверяем, что поле с ошибкой имеет класс is-invalid

    response = client.post('/phone_form', data={'phone': '7(800)555A35-35'})
    assert 'is-invalid' in response.data.decode('utf-8')  # Проверяем, что поле с ошибкой имеет класс is-invalid

def test_phone_field_no_invalid_class_on_valid_input(client):
    response = client.post('/phone_form', data={'phone': '+7 (900) 123-45-67'})
    assert 'is-invalid' not in response.data.decode('utf-8')  # Проверяем, что класс is-invalid НЕ применяется при правильном номере телефона
    
    response = client.post('/phone_form', data={'phone': '7(900)1234567'})
    assert 'is-invalid' not in response.data.decode('utf-8')  # Проверяем, что класс is-invalid НЕ применяется при правильном номере телефона