import os

from bs4 import BeautifulSoup
from flask import Blueprint, request, render_template, jsonify
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename

from applications.common.utils.http import fail_api, success_api, table_api
from applications.extensions import db
from applications.models import Post
from applications.common.utils.upload import upload_one

bp = Blueprint('home_post', __name__, url_prefix='/post')

def extract_text(content, max_length=100):
    """
    提取超文本内容的纯文本，并截取到指定长度后添加省略号。

    :param content: str, 超文本内容
    :param max_length: int, 截取的最大字符数，默认为100
    :return: str, 提取并截取后的纯文本
    """
    # 使用 BeautifulSoup 提取纯文本
    soup = BeautifulSoup(content, 'html.parser')
    text = soup.get_text(strip=True)  # 提取文本并去除首尾空格

    # 截取到指定长度，并在结尾补充 "..."
    if len(text) > max_length:
        return text[:max_length] + "..."
    return text

# 博客文章管理首页
@bp.get('/')
@login_required
def index():
    return render_template('home/post/list.html')


# 博客文章分页查询
@bp.get('/data')
@login_required
def data():
    title = request.args.get('title', type=str)
    filters = [Post.user_id == current_user.id]  # 限定为当前用户的文章

    if title:
        filters.append(Post.title.contains(title))

    query = Post.query.filter(*filters).order_by(Post.date_posted.desc()).layui_paginate()

    return table_api(
        data=[{
            'id': post.id,
            'title': post.title,
            'content': extract_text(post.content) if post.content else "无内容",
            'date_posted': post.date_posted,
            'cover': post.cover,
        } for post in query.items],
        count=query.total
    )


# 新增文章页面
@bp.get('/add')
@login_required
def add():
    return render_template('home/post/add.html')


# 保存新文章
# 保存新文章
@bp.route('/save', methods=['POST'])
@login_required
def save():
    # 获取表单数据
    title = request.form.get('title')
    content = request.form.get('content')
    cover = request.files.get('cover')  # 获取上传的文件

    # 校验标题和内容
    if not title or not content:
        return jsonify({'success': False, 'msg': '标题和内容不得为空'}), 400

    # 校验封面文件
    if cover:
        # 限制文件格式
        allowed_extensions = {'jpg', 'jpeg', 'png'}
        extension = cover.filename.rsplit('.', 1)[-1].lower()
        if extension not in allowed_extensions:
            return jsonify({'success': False, 'msg': '仅支持 jpg/png 格式的文件'}), 400

        # 保存文件到指定目录
        cover = request.files['cover']
        mime = extension
        file_url = upload_one(photo=cover, mime=mime)

    else:
        file_url = None  # 未上传封面
    # 保存到数据库
    post = Post(title=title, content=content, cover=file_url, user_id=current_user.id)
    db.session.add(post)
    db.session.commit()

    return success_api("成功上传")


# 编辑文章页面
@bp.get('/edit/<int:id>')
@login_required
def edit(id):
    post = Post.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    return render_template('home/post/edit.html', post=post)


# 更新文章
@bp.post('/update/<int:id>')
@login_required
def update(id):
    post = Post.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    title = request.form.get('title')
    content = request.form.get('content')
    cover = request.files.get('cover')

    post.title = title
    post.content = content
    # 校验封面文件
    # 校验封面文件
    if cover:
        # 限制文件格式
        allowed_extensions = {'jpg', 'jpeg', 'png'}
        extension = cover.filename.rsplit('.', 1)[-1].lower()
        if extension not in allowed_extensions:
            return jsonify({'success': False, 'msg': '仅支持 jpg/png 格式的文件'}), 400

        # 保存文件到指定目录
        cover = request.files['cover']
        mime = extension
        file_url = upload_one(photo=cover, mime=mime)
    else:
        file_url = None
    post.cover = file_url
    print(file_url)
    db.session.commit()
    return success_api(msg="文章更新成功")


# 删除文章
@bp.delete('/remove/<int:id>')
@login_required
def delete(id):
    post = Post.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    db.session.delete(post)
    db.session.commit()
    return success_api(msg="文章删除成功")


# 封面上传 API
@bp.post('/upload_cover')
@login_required
def upload_cover():
    if 'cover' in request.files:
        cover = request.files['cover']
        mime = request.files['cover'].content_type

        file_url = upload_one(photo=cover, mime=mime)
        res = {
            "msg": "封面上传成功",
            "code": 0,
            "success": True,
            "data": {
                "src": file_url
            }
        }
        return jsonify(res)
    return fail_api()
