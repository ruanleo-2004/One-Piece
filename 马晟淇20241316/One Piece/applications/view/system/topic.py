import datetime

from flask import Blueprint, request, render_template, jsonify
from flask_login import login_required

from applications.common.utils.http import fail_api, success_api, table_api
from applications.common.utils.upload import upload_one
from applications.extensions import db
from applications.models.blog_topic import TopicArticle
bp = Blueprint('topic', __name__, url_prefix='/topic')


# 篇章故事管理首页
@bp.get('/')
@login_required
def index():
    return render_template('system/topic/main.html')


# 篇章故事文章分页查询
@bp.get('/data')
@login_required
def data():
    # 筛选篇章故事标题
    title = request.args.get('title', type=str)
    filters = []

    if title:
        filters.append(TopicArticle.title.contains(title))

    query = TopicArticle.query.filter(*filters).order_by(TopicArticle.create_time.desc()).layui_paginate()

    return table_api(
        data=[{
            'id': article.id,
            'title': article.title,
            'link': article.link,
            'original_work': article.original_work,
            'anime': article.anime,
            'enable': '开启' if article.enable else '关闭',
            'create_time': article.create_time.strftime('%Y-%m-%d %H:%M:%S'),
        } for article in query.items],
        count=query.total
    )


# 新增篇章故事页面
@bp.get('/add')
@login_required
def add():
    return render_template('system/topic/add.html')


# 保存篇章故事文章
@bp.post('/save')
@login_required
def save():
    title = request.form.get('title')
    link = request.form.get('link')
    content = request.form.get('content')
    cover = request.files.get('cover')

    if not title or not link:
        return fail_api("标题或链接不得为空")

    if cover:
        allowed_extensions = {'jpg', 'jpeg', 'png'}
        extension = cover.filename.rsplit('.', 1)[-1].lower()
        if extension not in allowed_extensions:
            return fail_api("仅支持 jpg/png 格式的文件")

        mime = extension
        file_url = upload_one(photo=cover, mime=mime)
    else:
        file_url = None

    topic_article = TopicArticle(
        title=title,
        link=link,
        content=content,
        cover=file_url,
        enable=1
    )
    db.session.add(topic_article)
    db.session.commit()

    return success_api("篇章故事文章保存成功")


# 编辑篇章故事页面
@bp.get('/edit/<int:id>')
@login_required
def edit(id):
    topic = TopicArticle.query.get_or_404(id)
    return render_template('system/topic/edit.html', topic=topic)


# 更新篇章故事文章
@bp.post('/update/<int:id>')
@login_required
def update(id):
    article = TopicArticle.query.get_or_404(id)
    title = request.form.get('title')
    link = request.form.get('link')
    content = request.form.get('content')
    cover = request.files.get('cover')

    if not title or not link:
        return fail_api("标题或链接不得为空")

    if cover:
        allowed_extensions = {'jpg', 'jpeg', 'png'}
        extension = cover.filename.rsplit('.', 1)[-1].lower()
        if extension not in allowed_extensions:
            return fail_api("仅支持 jpg/png 格式的文件")

        mime = extension
        file_url = upload_one(photo=cover, mime=mime)
        article.cover = file_url

    article.title = title
    article.link = link
    article.content = content
    db.session.commit()

    return success_api("篇章故事文章更新成功")


# 删除篇章故事文章
@bp.delete('/remove/<int:id>')
@login_required
def remove(id):
    article = TopicArticle.query.get_or_404(id)
    db.session.delete(article)
    db.session.commit()
    return success_api("篇章故事文章删除成功")


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
