import datetime
from applications.extensions import db
from sqlalchemy.dialects.mysql import LONGTEXT
# 新闻模型
class NewsArticle(db.Model):
    __tablename__ = 'blog_news'

    id = db.Column(db.Integer, primary_key=True)

    # 新闻标题，不能为空
    title = db.Column(db.String(255), nullable=False)
    # 新闻发布日期，默认为当前时间
    release_date = db.Column(db.DateTime, default=datetime.datetime.now)
    # 新闻主分类名称，可为空
    category_name = db.Column(db.String(100), nullable=True)
    # 新闻子分类名称，可为空
    category_2_name = db.Column(db.String(100), nullable=True)
    # 在线文章路径，可为空
    link = db.Column(db.String(255), nullable=True)
    # 图片路径，可为空
    cover = db.Column(db.String(255), nullable=True)
    # 是否为最新新闻，默认为 False
    is_new = db.Column(db.Boolean, default=False)
    # 文章内容，使用富文本格式，可为空
    article = db.Column(LONGTEXT, nullable=True)
    # 是否开启，默认为 1（开启）
    enable = db.Column(db.Integer, default=1, comment='是否开启')
    # 创建时间，默认为当前时间
    create_time = db.Column(db.DateTime, default=datetime.datetime.now, comment='创建时间')
    # 更新时间，默认为当前时间，并在记录更新时自动更新
    update_time = db.Column(
        db.DateTime,
        default=datetime.datetime.now,
        onupdate=datetime.datetime.now,
        comment='更新时间'
    )

    # 定义对象的字符串表示
    def __repr__(self):
        return f"<NewsArticle {self.title}>"

