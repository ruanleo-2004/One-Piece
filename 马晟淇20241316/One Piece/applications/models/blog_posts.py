import datetime

from sqlalchemy.dialects.mysql import LONGTEXT

from applications.extensions import db
from applications.models.admin_user import User


# 博客文章模型
class Post(db.Model):
    __tablename__ = 'blog_posts'

    id = db.Column(db.Integer, primary_key=True)

    # 文章标题，不允许为空
    title = db.Column(db.String(100), nullable=False)
    # 封面图片路径，可为空
    cover = db.Column(db.String(255), nullable=True)
    # 文章内容，使用 MySQL 的 LONGTEXT 类型存储大文本数据
    content = db.Column(LONGTEXT, nullable=True)
    # 发布时间，默认使用 UTC 时间
    date_posted = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    # 用户ID，外键，关联到 admin_user 表的 id 字段，不允许为空
    user_id = db.Column(db.Integer, db.ForeignKey('admin_user.id'), nullable=False)
    # 是否开启，默认为 1（开启）
    enable = db.Column(db.Integer, default=1, comment='是否开启')
    # 创建时间，默认当前时间
    create_time = db.Column(db.DateTime, default=datetime.datetime.now, comment='创建时间')

    # 更新时间，默认当前时间，并在记录更新时自动更新
    update_time = db.Column(
        db.DateTime,
        default=datetime.datetime.now,
        onupdate=datetime.datetime.now,
        comment='更新时间'
    )
    def get_comment_count(self):
        # 延迟导入以避免循环依赖
        from applications.models.blog_posts import Comment
        return Comment.query.filter_by(post_id=self.id).count()
    # 获取文章作者
    def get_author(self):
        return User.query.get(self.user_id)

    # 定义对象的字符串表示
    def __repr__(self):
        return f"<Post(id={self.id}, title='{self.title}', date_posted='{self.date_posted}', user_id={self.user_id})>"
    
    # 为 Post 模型添加点赞计数实例方法
    def get_like_count(self):
        return self.likes.count()


# 评论模型
class Comment(db.Model):
    __tablename__ = 'blog_comments'

    id = db.Column(db.Integer, primary_key=True)
    # 评论内容，不允许为空
    content = db.Column(db.Text, nullable=False)
    # 评论时间，默认使用 UTC 时间
    date_posted = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    # 用户ID，外键，关联到 admin_user 表的 id 字段，不允许为空
    user_id = db.Column(db.Integer, db.ForeignKey('admin_user.id'), nullable=False)
    # 博客文章ID，外键，关联到 blog_posts 表的 id 字段，不允许为空
    post_id = db.Column(db.Integer, db.ForeignKey('blog_posts.id'), nullable=False)
    # 父评论ID，外键，关联到自身的 id 字段，允许为空（表示是顶级评论）
    parent_id = db.Column(db.Integer, db.ForeignKey('blog_comments.id'), nullable=True)
    # 是否开启，默认为 1（开启）
    enable = db.Column(db.Integer, default=1, comment='是否开启')
    # 创建时间，默认当前时间
    create_time = db.Column(db.DateTime, default=datetime.datetime.now, comment='创建时间')
    # 更新时间，默认当前时间，并在记录更新时自动更新
    update_time = db.Column(
        db.DateTime,
        default=datetime.datetime.now,
        onupdate=datetime.datetime.now,
        comment='更新时间'
    )
    # 与 User 模型建立关系，表示评论属于某个用户
    user = db.relationship('User', back_populates='comments')
    # 与 Post 模型建立关系，表示评论属于某篇博客文章
    post = db.relationship('Post', back_populates='comments')
    # 与自身建立关系，表示评论的回复
    replies = db.relationship('Comment', backref=db.backref('parent', remote_side=[id]), lazy='dynamic')

    # 定义对象的字符串表示
    def __repr__(self):
        return f"<Comment(id={self.id}, content='{self.content[:20]}...', date_posted='{self.date_posted}', user_id={self.user_id}, post_id={self.post_id}, parent_id={self.parent_id})>"


# 博客文章点赞模型
class PostLike(db.Model):
    __tablename__ = 'blog_post_likes'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('admin_user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('blog_posts.id'), nullable=False)
    date_liked = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    
    # 添加唯一约束，确保用户不能多次点赞同一篇文章
    __table_args__ = (db.UniqueConstraint('user_id', 'post_id', name='_user_post_like_uc'),)

# 在 User 模型中添加评论的反向关系
User.comments = db.relationship('Comment', back_populates='user')

# 在 Post 模型中添加评论的反向关系
Post.comments = db.relationship('Comment', back_populates='post')

# 在 Post 模型中添加点赞的关系
Post.likes = db.relationship('PostLike', backref='post', lazy='dynamic')

# 在 User 模型中添加文章的反向关系
User.posts = db.relationship('Post', backref='author', lazy='dynamic')

# 在 User 模型中添加点赞的关系
User.likes = db.relationship('PostLike', backref='user', lazy='dynamic')



# 为 User 模型添加点赞方法
def like_post(self, post):
    if not self.is_liking(post):
        like = PostLike(user_id=self.id, post_id=post.id)
        db.session.add(like)
        db.session.commit()

# 为 User 模型添加取消点赞方法
def unlike_post(self, post):
    like = PostLike.query.filter_by(user_id=self.id, post_id=post.id).first()
    if like:
        db.session.delete(like)
        db.session.commit()

# 为 User 模型添加检查是否已点赞的方法
def is_liking(self, post):
    return PostLike.query.filter_by(user_id=self.id, post_id=post.id).first() is not None

# 将方法添加到 User 模型
User.like_post = like_post
User.unlike_post = unlike_post
User.is_liking = is_liking
