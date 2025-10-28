from functools import reduce
from collections import namedtuple
import logging
import pytest
from datetime import datetime
import mysql.connector
from app import create_app
from app.models import db, Course
from app.repositories.course_repository import CourseRepository
from app.repositories.user_repository import  UserRepository
from app.repositories.category_repository import CategoryRepository
from app.repositories.image_repository import ImageRepository
from app.repositories.review_repository import ReviewRepository
from app.models import Review


TEST_DB_CONFIG = {
    'SQLALCHEMY_DATABASE_URI': 'mysql+mysqlconnector://root:123@localhost/lab6db2',
    'SQLALCHEMY_TRACK_MODIFICATIONS': False,
    'TESTING': True,
}


@pytest.fixture(scope='session')
def app():
    app = create_app(TEST_DB_CONFIG)
    return app

@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture(scope='session')
def db_session(app):
    with app.app_context():
        yield db


@pytest.fixture
def course_repository(db_session):
    return CourseRepository(db_session)

@pytest.fixture
def review_repository(db_session):
    return ReviewRepository(db_session)


@pytest.fixture
def existing_reviews(course_repository, review_repository):
    course = course_repository.get_course_by_id(1)
    if course is None:
        course = course_repository.add_course(
            id=1,
            title="Тестовый курс",
            description="Описание курса",
        )

    review_repository.db.session.query(Review).filter_by(course_id=course.id).delete()
    review_repository.db.session.commit()

    ratings = [0, 1, 2, 3, 4, 5, 5]
    created_reviews = []

    for user_id, rating in zip(range(1, 8), ratings):
        review = review_repository.add_review(
            course.id,
            user_id,
            rating,
            f"Тест отзыв от пользователя {user_id} с оценкой {rating}",
        )

        if review:
            created_reviews.append(review)

    yield created_reviews



# Извлекает список кортежей (рейтинг, дата)
def parse_reviews_from_html(html_data: str):
    reviews = []
    blocks = html_data.split('<div class="card mb-3">')[1:]  # пропускаем всё до первого отзыва

    for block in blocks:
        try:
            rating_part = block.split('Оценка:')[1]
            rating_str = rating_part.split('</span>')[1].strip().split('/')[0]
            rating = int(rating_str)

            date_part = block.split('—')[1].split('</small>')[0].strip()
            created_at = datetime.strptime(date_part, '%Y-%m-%d %H:%M')

            reviews.append((rating, created_at))
        except (IndexError, ValueError):
            continue  # пропускает некорректные блоки

    return reviews