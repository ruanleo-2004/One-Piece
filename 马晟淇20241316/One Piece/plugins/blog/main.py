from flask import render_template, Blueprint

from .views.about import about_bp
from .views.home_comment import bp as home_comment_bp
from .views.home_post import bp as home_post_bp
from .views.news import news_bp
from .views.post import post_bp
from .views.series import series_bp
from .views.topic import topic_bp
from .views.gallery import gallery_bp
from .views.user import user_bp

# 创建蓝图
blog_blueprint = Blueprint('blog', __name__, template_folder='templates', static_folder="static",
                           url_prefix="/blog")

blog_blueprint.register_blueprint(news_bp, url_prefix="/news")
blog_blueprint.register_blueprint(topic_bp, url_prefix="/topic")
blog_blueprint.register_blueprint(series_bp, url_prefix="/series")
blog_blueprint.register_blueprint(about_bp, url_prefix="/about")
blog_blueprint.register_blueprint(post_bp, url_prefix="/post")
blog_blueprint.register_blueprint(home_post_bp, url_prefix="/home/post")
blog_blueprint.register_blueprint(home_comment_bp, url_prefix="/home/comment")
blog_blueprint.register_blueprint(gallery_bp, url_prefix="/gallery")
blog_blueprint.register_blueprint(user_bp, url_prefix="/user")

@blog_blueprint.route("/")
def index():
    return render_template("index.html")
