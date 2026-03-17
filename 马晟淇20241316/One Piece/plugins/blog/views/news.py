import datetime

from flask import Blueprint, request, render_template

from applications.models.blog_news import NewsArticle
from ..schemas.blog_news import NewsArticleSchema

news_bp = Blueprint('news', __name__)


@news_bp.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    sort = request.args.get('sort', 'desc', type=str)  # 默认降序（最新在前）
    per_page = 24  # 每页显示文章数量

    # 根据排序参数决定排序方式
    if sort == 'asc':
        order = NewsArticle.create_time.asc()
    else:
        order = NewsArticle.create_time.desc()

    pagination = NewsArticle.query.filter_by(enable=1).order_by(order).paginate(page=page,
                                                                                per_page=per_page,
                                                                                error_out=False)
    articles = NewsArticleSchema(many=True).dump(pagination.items)

    return render_template('news/list.html', articles=articles, pagination=pagination, current_sort=sort)


@news_bp.route('/<int:id>')
def detail(id):
    article = NewsArticleSchema().dump(NewsArticle.query.get(id))
    if isinstance(article['release_date'], str):
        article['release_date'] = datetime.datetime.fromisoformat(article['release_date'])
    return render_template('news/item.html', article=article)
