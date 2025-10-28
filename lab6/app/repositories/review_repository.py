from ..models import Review, Course
from sqlalchemy import desc

class ReviewRepository:
    def __init__(self, db):
        self.db = db

    def get_latest_reviews_for_course(self, course_id, limit=5):
        return (
            self.db.session.query(Review)
            .filter(Review.course_id == course_id)
            .order_by(Review.created_at.desc())
            .limit(limit)
            .all()
        )

    def get_paginated_reviews(self, course_id, sort_by='newest'):
        query = self.db.select(Review).filter_by(course_id=course_id)

        if sort_by == 'positive':
            query = query.order_by(Review.rating.desc())
        elif sort_by == 'negative':
            query = query.order_by(Review.rating.asc())
        else:
            query = query.order_by(desc(Review.created_at))

        return self.db.paginate(query)

    def get_user_review(self, course_id, user_id):
        return self.db.session.query(Review).filter_by(course_id=course_id, user_id=user_id).first()

    def add_review(self, course_id, user_id, rating, text):
        existing = self.get_user_review(course_id, user_id)
        if existing:
            return None  # или обновление

        review = Review(course_id=course_id, user_id=user_id, rating=rating, text=text)
        self.db.session.add(review)

        # Обновление рейтинга курса
        course = self.db.session.get(Course, course_id)
        if course:
            course.rating_sum += rating
            course.rating_num += 1

        self.db.session.commit()
        return review
