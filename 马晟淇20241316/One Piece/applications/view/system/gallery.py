from flask import Blueprint, jsonify, request, render_template

from applications.extensions import db
from applications.models.blog_gallery import GalleryImage
from applications.common.utils import upload as upload_curd

bp = Blueprint('gallery', __name__, url_prefix='/gallery')


@bp.route('/')
def index():
    return render_template('system/gallery/main.html')


@bp.route('/data', methods=['GET'])
def get_data():
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 10))
    query = GalleryImage.query

    image_name = request.args.get('image_name')
    if image_name:
        query = query.filter(GalleryImage.image_name.like(f'%{image_name}%'))

    total = query.count()
    images = query.offset((page - 1) * limit).limit(limit).all()

    data = [{
        'id': image.id,
        'image_name': image.image_name,
        'image_path': image.image_path,
        'description': image.description,
        'url': image.url,
        'created_at': image.created_at.strftime('%Y-%m-%d %H:%M:%S')
    } for image in images]

    return jsonify({'code': 0, 'msg': '', 'count': total, 'data': data})


@bp.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        # 检查是否有文件上传
        if 'file' in request.files:
            photo = request.files['file']
            mime = request.files['file'].content_type
            file_url = upload_curd.upload_one(photo=photo, mime=mime)
            new_image = GalleryImage(
                image_name=request.form.get('image_name'),
                image_path=file_url,
                description=request.form.get('description'),
                url=request.form.get('url')
            )
        else:
            # 如果没有文件上传，使用表单中的图片路径
            data = request.get_json(silent=True) or request.form
            new_image = GalleryImage(
                image_name=data['image_name'],
                image_path=data['image_path'],
                description=data.get('description'),
                url=data.get('url')
            )
        db.session.add(new_image)
        db.session.commit()
        return jsonify({'success': True})
    return render_template('system/gallery/add.html')


@bp.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    image = GalleryImage.query.get(id)
    if not image:
        return jsonify({'success': False, 'message': '图片不存在'})

    if request.method == 'POST':
        # 检查是否有文件上传
        if 'file' in request.files:
            photo = request.files['file']
            mime = request.files['file'].content_type
            file_url = upload_curd.upload_one(photo=photo, mime=mime)
            image.image_name = request.form.get('image_name')
            image.image_path = file_url
            image.description = request.form.get('description')
            image.url = request.form.get('url')
        else:
            # 如果没有文件上传，使用表单中的图片路径
            data = request.get_json(silent=True) or request.form
            image.image_name = data['image_name']
            image.image_path = data['image_path']
            image.description = data.get('description')
            image.url = data.get('url')
        db.session.commit()
        return jsonify({'success': True})

    return render_template('system/gallery/edit.html', image=image,id=id)


@bp.route('/remove/<int:image_id>', methods=['DELETE'])
def remove(image_id):
    image = GalleryImage.query.get(image_id)
    if not image:
        return jsonify({'success': False, 'message': '图片不存在'})
    db.session.delete(image)
    db.session.commit()
    return jsonify({'success': True})
