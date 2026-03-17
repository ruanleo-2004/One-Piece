import datetime

from applications.extensions import db


# 系列模型
class Series(db.Model):
    __tablename__ = "blog_series"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # 系列名称，不允许为空
    series = db.Column(db.String(255), nullable=False)
    # 类型字段，表示系列的类别
    # choices=[('令和', 'linghe'), ('昭和', 'zhaohe'), ('平成', 'pingcheng')]
    type = db.Column(db.String(255), nullable=False)
    # 系列作品的名称，不允许为空
    name = db.Column(db.String(255), nullable=False)
    # 系列的年份，可为空
    year = db.Column(db.String(4), nullable=True)
    # 图片的 URL，可为空
    cover = db.Column(db.String(255), nullable=True)
    # 作品的绝对 URL，用于外部链接或内部导航，不允许为空且必须唯一
    link = db.Column(db.String(255), nullable=True)
    # 是否为外部资源，布尔类型，默认值为 False
    is_external = db.Column(db.Boolean, default=False)
    # 是否开启，默认值为 1（开启）
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

    # 定义对象的字符串表示
    def __repr__(self):
        return f"<Series(name={self.name}, year={self.year})>"
