from datetime import datetime
from .testcase_set import db


class TestCase(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    test_case_set_id = db.Column(db.Integer, db.ForeignKey('test_case_set.id'), nullable=False)
    description = db.Column(db.Text, nullable=False)
    step = db.Column(db.Text)
    expected_result = db.Column(db.Text)
    status = db.Column(db.String(20), default='Not Executed')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<TestCase {self.id} - {self.description[:20]}>'
