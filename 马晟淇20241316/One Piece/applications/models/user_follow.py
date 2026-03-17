import datetime
from applications.extensions import db
from applications.models.admin_user import User


# 用户关注关系模型
class UserFollow(db.Model):
    __tablename__ = 'user_follow'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='关注关系ID')
    follower_id = db.Column(db.Integer, db.ForeignKey('admin_user.id'), nullable=False, comment='关注者ID')
    followed_id = db.Column(db.Integer, db.ForeignKey('admin_user.id'), nullable=False, comment='被关注者ID')
    create_time = db.Column(db.DateTime, default=datetime.datetime.now, comment='关注时间')
    
    # 添加唯一约束，确保一个用户不能重复关注另一个用户
    __table_args__ = (
        db.UniqueConstraint('follower_id', 'followed_id', name='unique_follow_relation'),
    )
    
    # 定义与用户模型的关系
    follower = db.relationship(User, foreign_keys=[follower_id], backref=db.backref('followed', lazy='dynamic'))
    followed = db.relationship(User, foreign_keys=[followed_id], backref=db.backref('followers', lazy='dynamic'))
    
    def __repr__(self):
        return f"<UserFollow(follower_id={self.follower_id}, followed_id={self.followed_id})>"
