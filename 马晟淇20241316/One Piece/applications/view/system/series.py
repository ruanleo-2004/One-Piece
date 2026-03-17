from applications.models.blog_series import Series
from flask import Blueprint, request, render_template, jsonify
from flask_login import login_required

from applications.common.utils.http import fail_api, success_api, table_api
from applications.common.utils.upload import upload_one
from applications.extensions import db

bp = Blueprint('series', __name__, url_prefix='/series')


# 系列管理首页
@bp.get('/')
@login_required
def index():
    return render_template('system/series/main.html')


# 系列分页查询
@bp.get('/data')
@login_required
def data():
    # 筛选条件
    name = request.args.get('name', type=str)
    filters = []

    if name:
        filters.append(Series.name.contains(name))

    query = Series.query.filter(*filters).order_by(-Series.create_time.desc()).layui_paginate()

    return table_api(
        data=[{
            'id': series.id,
            'series': series.series,
            'type': series.type,
            'name': series.name,
            'year': series.year,
            'enable': '开启' if series.enable else '关闭',
            'create_time': series.create_time.strftime('%Y-%m-%d'),
        } for series in query.items],
        count=query.total
    )


# 新增系列页面
@bp.get('/add')
@login_required
def add():
    return render_template('system/series/add.html')


# 保存系列
@bp.post('/save')
@login_required
def save():
    series = request.form.get('series')
    type = request.form.get('type')
    name = request.form.get('name')
    year = request.form.get('year')
    image_url = request.form.get('image_url')
    absolute_url = request.form.get('absolute_url')
    is_external = request.form.get('is_external', 'false') == 'true'

    if not series or not type or not name or not absolute_url:
        return fail_api("系列、类型、名称或链接不得为空")

    new_series = Series(
        series=series,
        type=type,
        name=name,
        year=year,
        image_url=image_url,
        absolute_url=absolute_url,
        is_external=is_external,
        enable=1
    )
    db.session.add(new_series)
    db.session.commit()

    return success_api("系列保存成功")


# 编辑系列页面
@bp.get('/edit/<int:id>')
@login_required
def edit(id):
    series = Series.query.get_or_404(id)
    return render_template('system/series/edit.html', series=series)


# 更新系列
@bp.post('/update/<int:id>')
@login_required
def update(id):
    series = Series.query.get_or_404(id)
    series_name = request.form.get('series')
    type = request.form.get('type')
    name = request.form.get('name')
    year = request.form.get('year')
    image_url = request.form.get('image_url')
    absolute_url = request.form.get('absolute_url')
    is_external = request.form.get('is_external', 'false') == 'true'

    if not series_name or not type or not name or not absolute_url:
        return fail_api("系列、类型、名称或链接不得为空")

    series.series = series_name
    series.type = type
    series.name = name
    series.year = year
    series.image_url = image_url
    series.absolute_url = absolute_url
    series.is_external = is_external
    db.session.commit()

    return success_api("系列更新成功")


# 删除系列
@bp.delete('/remove/<int:id>')
@login_required
def delete(id):
    series = Series.query.get_or_404(id)
    db.session.delete(series)
    db.session.commit()
    return success_api("系列删除成功")


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
