from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class TestCaseSet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    test_cases = db.relationship('TestCase', backref='test_case_set', lazy=True, cascade="all, delete-orphan")

    # Nâng cấp: Liên kết với người dùng
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    is_public = db.Column(db.Boolean, default=False)  # Testcase có công khai không

    def __repr__(self):
        return f'<TestCaseSet {self.name}>'
