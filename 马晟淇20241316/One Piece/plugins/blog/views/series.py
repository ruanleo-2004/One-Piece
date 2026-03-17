from flask import Blueprint, render_template, request
from applications.models import Series

# 创建蓝图
series_bp = Blueprint(
    'series',
    __name__,
    template_folder='templates/series',
    static_folder='static/series',
    url_prefix='/series'
)


@series_bp.route('/')
def index():
    """系列列表页"""
    # 获取系列类型参数
    series_type = request.args.get('series_type', type=str)

    # 获取分页参数
    page = request.args.get('page', 1, type=int)
    per_page = 36  # 每页展示的系列数

    # 构建查询
    query = Series.query.filter_by(enable=1)
    if series_type:
        query = query.filter(Series.series == series_type)

    pagination = query.order_by(Series.year.desc(), Series.create_time.desc()) \
        .paginate(page=page, per_page=per_page, error_out=False)

    series_list = pagination.items

    return render_template(
        'series/list.html',
        series_list=series_list,
        pagination=pagination,
        series_type=series_type
    )
