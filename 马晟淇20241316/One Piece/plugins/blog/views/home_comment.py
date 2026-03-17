from flask import render_template, request, redirect, url_for, flash, Blueprint
from flask_login import login_required, current_user

from applications.models.blog_posts import Comment, Post, db

bp = Blueprint('home_comment', __name__, url_prefix='/comment')


# 评论管理视图
@bp.route('/', methods=['GET', 'POST'])
@login_required
def manage_comments():
    # 获取当前用户的所有评论
    page = request.args.get('page', 1, type=int)
    filter_title = request.args.get('filter_title', '', type=str)  # 博客标题筛选
    comments_query = Comment.query.filter_by(user_id=current_user.id)

    # 如果有博客标题筛选条件
    if filter_title:
        comments_query = comments_query.join(Post).filter(Post.title.like(f'%{filter_title}%'))

    comments = comments_query.order_by(Comment.date_posted.desc()).paginate(page=page, per_page=10)

    return render_template('home/comment/list.html', comments=comments, filter_title=filter_title)


# 删除评论视图
@bp.route('/<int:comment_id>/delete', methods=['POST'])
@login_required
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)

    # 检查是否为当前用户的评论
    if comment.user_id != current_user.id:
        flash('你没有权限删除这条评论', 'danger')
        return redirect(url_for('blog.home_comment.manage_comments'))

    db.session.delete(comment)
    db.session.commit()
    flash('评论已删除', 'success')
    return redirect(url_for('blog.home_comment.manage_comments'))
