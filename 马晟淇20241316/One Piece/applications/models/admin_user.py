import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from applications.extensions import db


class User(db.Model, UserMixin):
    __tablename__ = 'admin_user'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='用户ID')
    username = db.Column(db.String(20), comment='用户名')
    realname = db.Column(db.String(20), comment='真实名字')
    avatar = db.Column(db.String(255), comment='头像', default="/static/system/admin/images/avatar.jpg")
    remark = db.Column(db.String(255), comment='备注')
    password_hash = db.Column(db.String(128), comment='哈希密码')
    enable = db.Column(db.Integer, default=1, comment='启用')
    dept_id = db.Column(db.Integer, comment='部门id')
    create_at = db.Column(db.DateTime, default=datetime.datetime.now, comment='创建时间')
    update_at = db.Column(db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now, comment='创建时间')
    role = db.relationship('Role', secondary="admin_user_role", backref=db.backref('user'), lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def validate_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    # 关注功能相关方法
    def is_following(self, user):
        from applications.models.user_follow import UserFollow
        return UserFollow.query.filter_by(follower_id=self.id, followed_id=user.id).first() is not None
    
    def follow(self, user):
        from applications.models.user_follow import UserFollow
        if not self.is_following(user):
            uf = UserFollow(follower_id=self.id, followed_id=user.id)
            db.session.add(uf)
            db.session.commit()
    
    def unfollow(self, user):
        from applications.models.user_follow import UserFollow
        uf = UserFollow.query.filter_by(follower_id=self.id, followed_id=user.id).first()
        if uf:
            db.session.delete(uf)
            db.session.commit()
    
    def followed_users(self):
        from applications.models.user_follow import UserFollow
        return User.query.join(UserFollow, UserFollow.followed_id == User.id).filter(UserFollow.follower_id == self.id)
    
    # 收藏功能相关方法
    def is_favoriting(self, post):
        from applications.models.user_favorite import UserFavorite
        return UserFavorite.query.filter_by(user_id=self.id, post_id=post.id).first() is not None
    
    def favorite(self, post):
        from applications.models.user_favorite import UserFavorite
        if not self.is_favoriting(post):
            uf = UserFavorite(user_id=self.id, post_id=post.id)
            db.session.add(uf)
            db.session.commit()
    
    def unfavorite(self, post):
        from applications.models.user_favorite import UserFavorite
        uf = UserFavorite.query.filter_by(user_id=self.id, post_id=post.id).first()
        if uf:
            db.session.delete(uf)
            db.session.commit()
    
    def favorite_posts(self):
        from applications.models.user_favorite import UserFavorite
        from applications.models.blog_posts import Post
        return Post.query.join(UserFavorite, UserFavorite.post_id == Post.id).filter(UserFavorite.user_id == self.id)

