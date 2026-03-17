import datetime
from applications.extensions import db
from applications.models.admin_user import User
from applications.models.blog_posts import Post


# 用户收藏关系模型
class UserFavorite(db.Model):
    __tablename__ = 'user_favorite'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='收藏关系ID')
    user_id = db.Column(db.Integer, db.ForeignKey('admin_user.id'), nullable=False, comment='用户ID')
    post_id = db.Column(db.Integer, db.ForeignKey('blog_posts.id'), nullable=False, comment='文章ID')
    create_time = db.Column(db.DateTime, default=datetime.datetime.now, comment='收藏时间')
    
    # 定义表参数
    __table_args__ = (
        db.UniqueConstraint('user_id', 'post_id', name='unique_favorite_relation'),
    )
    
    # 定义与用户模型的关系
    user = db.relationship(User, foreign_keys=[user_id], backref=db.backref('favorites', lazy='dynamic'))
    # 定义与文章模型的关系
    post = db.relationship(Post, foreign_keys=[post_id], backref=db.backref('favorited_by', lazy='dynamic'))
    
    def __repr__(self):
        return f"<UserFavorite(user_id={self.user_id}, post_id={self.post_id})>"
