from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow_sqlalchemy.fields import fields

from applications.extensions import db
from applications.models.blog_posts import Post, Comment


class PostSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Post
        sqla_session = db.session
        load_instance = True  # 支持将反序列化后的数据直接转为模型实例
        include_fk = True  # 包含外键字段（如有）

    create_time = fields.DateTime(format='%Y-%m-%d %H:%M:%S')
    update_time = fields.DateTime(format='%Y-%m-%d %H:%M:%S')


class CommentSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Comment
        sqla_session = db.session
        load_instance = True  # 支持将反序列化后的数据直接转为模型实例
        include_fk = True  # 包含外键字段（如有）

    create_time = fields.DateTime(format='%Y-%m-%d %H:%M:%S')
    update_time = fields.DateTime(format='%Y-%m-%d %H:%M:%S')
