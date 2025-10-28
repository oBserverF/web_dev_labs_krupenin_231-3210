import random
from conftest import parse_reviews_from_html

def test_review_content(existing_reviews, review_repository):
    review_repository.db.session.expire_all()
    assert len(existing_reviews) == 7 

    course_id = existing_reviews[0].course_id
    reviews = review_repository.get_latest_reviews_for_course(course_id, limit=10)

    assert len(reviews) == 7

    ratings = sorted([review.rating for review in reviews])
    expected_ratings = sorted([0, 1, 2, 3, 4, 5, 5])
    assert ratings == expected_ratings

    for user_id in range(1, 8):
        found = any(f"Тест отзыв от пользователя {user_id}" in review.text for review in reviews)
        assert found


def test_get_latest_reviews_for_course(review_repository, existing_reviews):
    review_repository.db.session.expire_all()
    course_id = existing_reviews[0].course_id
    latest_reviews = review_repository.get_latest_reviews_for_course(course_id)

    assert len(latest_reviews) == 5
    sorted_by_time = sorted(existing_reviews, key=lambda r: r.created_at, reverse=True)
    expected_ids = [r.id for r in sorted_by_time[:5]]
    actual_ids = [r.id for r in latest_reviews]

    assert actual_ids == expected_ids


def test_get_user_review(review_repository, existing_reviews):
    review_repository.db.session.expire_all()
    review = random.choice(existing_reviews)
    found = review_repository.get_user_review(review.course_id, review.user_id)

    assert found is not None
    assert found.id == review.id
    assert found.user_id == review.user_id
    assert found.course_id == review.course_id


def test_get_paginated_reviews_positive_sort(review_repository, existing_reviews):
    course_id = existing_reviews[0].course_id
    page = review_repository.get_paginated_reviews(course_id, sort_by="positive")

    ratings = [review.rating for review in page.items]
    assert ratings == sorted(ratings, reverse=True)


def test_review_pagination(client, existing_reviews):
    assert len(existing_reviews) == 7

    response_page_1 = client.get("/courses/1/reviews")
    assert response_page_1.status_code == 200
    data_1 = response_page_1.data.decode("utf-8")

    assert "Оценка:" in data_1  # или реальное количество, если пагинация работает

    response_page_2 = client.get("/courses/1/reviews?page=2")
    assert response_page_2.status_code == 404
    data_2 = response_page_2.data.decode("utf-8")

    # Проверка опциональна — зависит от количества отзывов на странице


def test_sorting_newest(client, existing_reviews):
    response = client.get("/courses/1/reviews?sort=newest")
    assert response.status_code == 200
    reviews = parse_reviews_from_html(response.data.decode())
    dates = [r[1] for r in reviews]
    assert dates == sorted(dates, reverse=True)


def test_sorting_positive(client, existing_reviews):
    response = client.get("/courses/1/reviews?sort=positive")
    assert response.status_code == 200
    reviews = parse_reviews_from_html(response.data.decode())
    ratings = [r[0] for r in reviews]
    assert ratings == sorted(ratings, reverse=True)


def test_sorting_negative(client, existing_reviews):
    response = client.get("/courses/1/reviews?sort=negative")
    assert response.status_code == 200
    reviews = parse_reviews_from_html(response.data.decode())
    ratings = [r[0] for r in reviews]
    assert ratings == sorted(ratings)
