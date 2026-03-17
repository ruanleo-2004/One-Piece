from flask import Blueprint, render_template, jsonify, request
from sqlalchemy.sql import func

from applications.models.blog_gallery import GalleryImage

gallery_bp = Blueprint('gallery', __name__)


@gallery_bp.route('/')
def index():
    return render_template("gallery/gallery.html")


@gallery_bp.route('/get_images')
def get_images():
    # 获取分页参数
    page = request.args.get('page', 1, type=int)
    per_page = 36  # 每页显示36张图片
    
    # 获取排序参数
    sort = request.args.get('sort', 'desc', type=str)
    
    # 根据排序参数决定排序方式
    if sort == 'asc':
        order = GalleryImage.created_at.asc()
    else:
        order = GalleryImage.created_at.desc()
    
    # 获取分页数据，按创建时间排序
    pagination = GalleryImage.query.order_by(order).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    # 处理图片数据
    image_data = [{
        'image_name': image.image_name,
        'image_path': image.image_path,
        'description': image.description,
        'url': image.url
    } for image in pagination.items]
    
    # 返回包含分页信息的完整数据
    return jsonify({
        'images': image_data,
        'pagination': {
            'page': pagination.page,
            'per_page': pagination.per_page,
            'total': pagination.total,
            'pages': pagination.pages,
            'has_prev': pagination.has_prev,
            'has_next': pagination.has_next
        }
    })
