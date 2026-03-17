
import datetime

from flask import Blueprint, request, render_template, jsonify
from flask_login import login_required

from applications.common.utils.http import fail_api, success_api, table_api
from applications.common.utils.upload import upload_one
from applications.extensions import db
from applications.models.blog_news import NewsArticle

bp = Blueprint('news_article', __name__, url_prefix='/news')


# 新闻管理首页
@bp.get('/')
@login_required
def index():
    return render_template('system/news/main.html')


# 新闻文章分页查询
@bp.get('/data')
@login_required
def data():
    # 筛选新闻标题
    title = request.args.get('title', type=str)
    filters = []

    if title:
        filters.append(NewsArticle.title.contains(title))

    query = NewsArticle.query.filter(*filters).order_by(NewsArticle.create_time.desc()).layui_paginate()

    return table_api(
        data=[{
            'id': article.id,
            'title': article.title,
            'category_name': article.category_name,
            'release_date': article.release_date.strftime('%Y-%m-%d') if article.release_date else '',
            'is_new': '是' if article.is_new else '否',
            'enable': '开启' if article.enable else '关闭',
        } for article in query.items],
        count=query.total
    )


# 新增新闻页面
@bp.get('/add')
@login_required
def add():
    return render_template('system/news/add.html')


# 保存新闻文章
@bp.post('/save')
@login_required
def save():
    title = request.form.get('title')
    category_name = request.form.get('category_name')
    content = request.form.get('article')
    release_date = request.form.get('release_date')
    is_new = request.form.get('is_new', 'false') == 'true'
    cover = request.files.get('cover')

    if not title or not content:
        return fail_api("标题或内容不得为空")

    if cover:
        allowed_extensions = {'jpg', 'jpeg', 'png'}
        extension = cover.filename.rsplit('.', 1)[-1].lower()
        if extension not in allowed_extensions:
            return fail_api("仅支持 jpg/png 格式的文件")

        mime = extension
        file_url = upload_one(photo=cover, mime=mime)
    else:
        file_url = None

    news_article = NewsArticle(
        title=title,
        category_name=category_name,
        article=content,
        release_date=datetime.datetime.strptime(release_date, '%Y-%m-%d') if release_date else None,
        is_new=is_new,
        cover=file_url,
        enable=1
    )
    db.session.add(news_article)
    db.session.commit()

    return success_api("新闻文章保存成功")


# 编辑新闻页面
@bp.get('/edit/<int:id>')
@login_required
def edit(id):
    article = NewsArticle.query.get_or_404(id)
    return render_template('system/news/edit.html', article=article)


# 更新新闻文章
@bp.post('/update/<int:id>')
@login_required
def update(id):
    article = NewsArticle.query.get_or_404(id)
    title = request.form.get('title')
    category_name = request.form.get('category_name')
    content = request.form.get('article')
    release_date = request.form.get('release_date')
    is_new = request.form.get('is_new', 'false') == 'true'
    cover = request.files.get('cover')

    if not title :
        return fail_api("标题不得为空")

    if cover:
        allowed_extensions = {'jpg', 'jpeg', 'png'}
        extension = cover.filename.rsplit('.', 1)[-1].lower()
        if extension not in allowed_extensions:
            return fail_api("仅支持 jpg/png 格式的文件")

        mime = extension
        file_url = upload_one(photo=cover, mime=mime)
        article.cover = file_url

    article.title = title
    article.category_name = category_name
    article.article = content
    article.release_date = datetime.datetime.strptime(release_date, '%Y-%m-%d') if release_date else None
    article.is_new = is_new
    db.session.commit()

    return success_api("新闻文章更新成功")


# 删除新闻文章
@bp.delete('/remove/<int:id>')
@login_required
def delete(id):
    article = NewsArticle.query.get_or_404(id)
    db.session.delete(article)
    db.session.commit()
    return success_api("新闻文章删除成功")


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

