import datetime
from applications.extensions import db
from sqlalchemy.dialects.mysql import LONGTEXT

# 篇章故事模型
class TopicArticle(db.Model):

    __tablename__ = "blog_topic"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # 篇章故事标题，不允许为空
    title = db.Column(db.String(512), nullable=False)
    # 篇章故事链接，字符串类型，不允许为空且必须唯一，用于指向篇章故事的访问地址
    link = db.Column(db.String(512), nullable=False)
    # 篇章故事封面图片的路径，可为空
    cover = db.Column(db.String(512), nullable=True)
    # 篇章故事内容，使用 `LONGTEXT` 类型存储大量文本数据，可为空
    content = db.Column(LONGTEXT, nullable=True)
    # 原作信息
    original_work = db.Column(db.String(255), nullable=True)
    # 动画信息
    anime = db.Column(db.String(255), nullable=True)
    # 是否开启，整型字段，默认值为 1（开启）
    enable = db.Column(db.Integer, comment='是否开启', default=1)
    # 创建时间，默认当前时间
    create_time = db.Column(
        db.DateTime,
        default=datetime.datetime.now,
        comment='创建时间'
    )
    # 更新时间，默认当前时间，并在记录更新时自动刷新
    update_time = db.Column(
        db.DateTime,
        default=datetime.datetime.now,
        onupdate=datetime.datetime.now,
        comment='更新时间'
    )
    # 定义对象的字符串表示，用于调试或日志
    def __repr__(self):
        return f"<Article(title={self.title}, link={self.link})>"
