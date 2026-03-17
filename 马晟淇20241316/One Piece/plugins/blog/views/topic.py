import datetime

from bs4 import BeautifulSoup
from flask import Blueprint, render_template, request

from applications.models import TopicArticle
from ..schemas.blog_topic import TopicArticleSchema
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
# 创建蓝图
topic_bp = Blueprint(
    'topic',
    __name__,
    template_folder='templates/topic',
    static_folder='static/topic',
    url_prefix='/topic'
)


@topic_bp.route('/')
def index():
    """文章列表页"""
    page = request.args.get('page', 1, type=int)
    sort = request.args.get('sort', 'desc', type=str)  # 默认降序（最新在前）
    per_page = 12  # 每页展示的文章数量

    # 根据排序参数决定排序方式
    if sort == 'asc':
        order = TopicArticle.create_time.asc()
    else:
        order = TopicArticle.create_time.desc()

    pagination = TopicArticle.query.filter_by(enable=1) \
        .order_by(order) \
        .paginate(page=page, per_page=per_page, error_out=False)

    articles = pagination.items
    for i in articles:
        i.content = extract_text(i.content)
    return render_template('topic/list.html', articles=articles, pagination=pagination, current_sort=sort)


@topic_bp.route('/<int:id>')
def item(id):
    article = TopicArticleSchema().dump(TopicArticle.query.get(id))
    if isinstance(article['create_time'], str):
        article['create_time'] = datetime.datetime.fromisoformat(article['create_time'])

    return render_template('topic/item.html', article=article)
