# models.py
from datetime import datetime

from applications.extensions import db


class Feedback(db.Model):
    __tablename__ = 'blog_feedback'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(15), nullable=True)
    category = db.Column(db.String(50), nullable=False)
    message = db.Column(db.Text, nullable=False)
    attachment = db.Column(db.String(200), nullable=True)  # 保存附件路径
    agree = db.Column(db.Boolean, nullable=False, default=False)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Feedback {self.name} - {self.category}>"
