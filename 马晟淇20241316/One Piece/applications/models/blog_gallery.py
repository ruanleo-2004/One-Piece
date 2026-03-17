# models.py

from applications.extensions import db


class GalleryImage(db.Model):
    __tablename__ = 'blog_gallery'
    id = db.Column(db.Integer, primary_key=True)
    image_name = db.Column(db.String(100), nullable=False)  # 图片文件名
    image_path = db.Column(db.String(200), nullable=False)  # 图片的存储路径
    description = db.Column(db.String(500), nullable=True)  # 图片的描述信息
    url = db.Column(db.String(500), nullable=True)  # 官网链接地址
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.now())  # 创建时间

    def __repr__(self):
        return f"<GalleryImage {self.image_name}>"
