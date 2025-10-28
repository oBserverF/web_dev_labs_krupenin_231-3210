def test_posts_index(client):
    response = client.get("/posts")
    assert response.status_code == 200
    assert "Последние посты" in response.text

def test_about_index(client):
    response = client.get("/about")
    assert response.status_code == 200
    assert "Об авторе" in response.text

def test_post_index(client):
    response = client.get("/posts/0")
    assert response.status_code == 200
    assert "Оставьте комментарий" in response.text

def test_main_index(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "Задание к лабораторной работе" in response.text

def test_posts_index_template(client, captured_templates, mocker, posts_list):
    with captured_templates as templates:
        mocker.patch(
            "app.posts_list",
            return_value=posts_list,
            autospec=True
        )
        
        _ = client.get('/posts')
        assert len(templates) == 1
        template, context = templates[0]
        assert template.name == 'posts.html'
        assert context['title'] == 'Посты'
        assert len(context['posts']) == 1

def test_index_template(client, captured_templates):
    with captured_templates as templates:
        response = client.get("/")
        assert response.status_code == 200
        assert "Задание к лабораторной работе" in response.text
        assert len(templates) == 1
        template, context = templates[0]
        assert template.name == "index.html"

def test_about_template(client, captured_templates):
    with captured_templates as templates:
        response = client.get("/about")
        assert response.status_code == 200
        assert "Об авторе" in response.text
        assert len(templates) == 1
        template, context = templates[0]
        assert template.name == "about.html"
        assert context['title'] == "Об авторе"

def test_post_detail_template(client, captured_templates, mocker, posts_list):
    mocker.patch(
        "app.posts_list",
        return_value=posts_list,
        autospec=True
    )
    with captured_templates as templates:
        response = client.get("/posts/0")
        assert response.status_code == 200
        assert "Оставьте комментарий" in response.text
        assert len(templates) == 1
        template, context = templates[0]
        assert template.name == 'post.html'
        assert context['title'] == posts_list[0]['title']
        assert context['post'] == posts_list[0]

def test_post_detail_content(client, mocker, posts_list):
    mocker.patch(
        "app.posts_list",
        return_value=posts_list,
        autospec=True
    )
    response = client.get("/posts/0")
    post = posts_list[0]
    assert post['title'] in response.text
    assert post['text'] in response.text
    assert post['author'] in response.text

def test_post_detail_has_image(client, mocker, posts_list):
    mocker.patch(
        "app.posts_list",
        return_value=posts_list,
        autospec=True
    )
    response = client.get("/posts/0")
    assert posts_list[0]['image_id'] in response.text

def test_post_date_format(client, mocker, posts_list):
    mocker.patch(
        "app.posts_list",
        return_value=posts_list,
        autospec=True
    )
    response = client.get("/posts/0")
    assert '10.03.2025' in response.text

def test_post_not_found(client, mocker, posts_list):
    mocker.patch(
        "app.posts_list",
        return_value=posts_list,
        autospec=True
    )
    response = client.get("/posts/999")
    assert response.status_code == 404

def test_post_not_found_invalid_url(client):
    response = client.get("/posts/ashdaaa")
    assert response.status_code == 404

def test_post_not_found_negative_id(client):
    response = client.get("/posts/-1")
    assert response.status_code == 404

def test_posts_index_has_post_links(client, mocker, posts_list):
    mocker.patch(
        "app.posts_list",
        return_value=posts_list,
        autospec=True
    )
    response = client.get("/posts")
    assert f'href="/posts/0"' in response.text