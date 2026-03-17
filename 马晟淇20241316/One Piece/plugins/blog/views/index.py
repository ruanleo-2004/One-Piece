from flask import Blueprint, request, render_template

from applications.models.blog_news import NewsArticle
from ..schemas.blog_news import NewsArticleSchema

news_bp = Blueprint('index', __name__)


@news_bp.route('/')
def news():
    page = request.args.get('page', 1, type=int)
    per_page = 36  # 每页显示文章数量
    pagination = NewsArticle.query.filter_by(enable=1).order_by(NewsArticle.release_date.desc()).paginate(page=page,
                                                                                                          per_page=per_page,
                                                                                                          error_out=False)
    articles = NewsArticleSchema(many=True).dump(pagination.items)

    return render_template('news/newsList.html', articles=articles, pagination=pagination)
