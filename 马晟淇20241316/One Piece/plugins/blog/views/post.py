from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import current_user, login_required
from bs4 import BeautifulSoup
from sqlalchemy import or_
from applications.models.blog_posts import Post, Comment, db
from applications.models.admin_user import User

post_bp = Blueprint('post', __name__, url_prefix='/post')


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


@post_bp.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '', type=str).strip()
    author = request.args.get('author', '', type=str).strip()
    
    # 构建查询
    query = Post.query.filter_by(enable=1)
    
    # 应用搜索过滤
    if search:
        query = query.filter(
            or_(
                Post.title.contains(search),
                Post.content.contains(search)
            )
        )
    
    # 应用作者过滤
    if author:
        query = query.join(User).filter(User.realname.contains(author))
    
    # 排序和分页
    posts = query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=6)

    for post in posts:
        post.content = extract_text(post.content) if post.content else "无内容"
    return render_template('post/list.html', posts=posts, search=search, author=author)


@post_bp.route('/<int:post_id>')
def detail(post_id):
    post = Post.query.filter_by(id=post_id, enable=1).first_or_404()
    return render_template('post/item.html', post=post)


@post_bp.route('/<int:post_id>/comment', methods=['POST'])
@login_required
def add_comment(post_id):
    post = Post.query.filter_by(id=post_id, enable=1).first_or_404()
    content = request.form.get('content')
    if not content.strip():
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'code': 400, 'message': '评论内容不能为空'})
        flash('评论内容不能为空', 'danger')
        return redirect(url_for('blog.post.detail', post_id=post_id))

    comment = Comment(content=content, user_id=current_user.id, post_id=post.id)
    db.session.add(comment)
    db.session.commit()
    
    # 如果是AJAX请求，返回新评论的HTML片段
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render_template('post/comment.html', comment=comment, current_user=current_user)
    
    flash('评论已成功提交', 'success')
    return redirect(url_for('blog.post.detail', post_id=post_id))


@post_bp.route('/<int:post_id>/comment/<int:comment_id>/reply', methods=['POST'])
@login_required
def reply_comment(post_id, comment_id):
    post = Post.query.filter_by(id=post_id, enable=1).first_or_404()
    parent_comment = Comment.query.get_or_404(comment_id)
    content = request.form.get('content')
    if not content.strip():
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'code': 400, 'message': '回复内容不能为空'})
        flash('回复内容不能为空', 'danger')
        return redirect(url_for('blog.post.detail', post_id=post_id))

    reply = Comment(content=content, user_id=current_user.id, post_id=post.id, parent_id=parent_comment.id)
    db.session.add(reply)
    db.session.commit()
    
    # 如果是AJAX请求，返回新回复的HTML片段
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render_template('post/comment.html', comment=reply, current_user=current_user)
    
    flash('回复已成功提交', 'success')
    return redirect(url_for('blog.post.detail', post_id=post_id))


@post_bp.route('/comment/<int:comment_id>/delete', methods=['POST'])
@login_required
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    post_id = comment.post_id

    # 检查是否为当前用户的评论
    if comment.user_id != current_user.id:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'code': 403, 'message': '你没有权限删除这条评论'})
        flash('你没有权限删除这条评论', 'danger')
        return redirect(url_for('blog.post.detail', post_id=post_id))

    # 删除评论及其所有回复
    delete_comment_tree(comment)
    db.session.commit()
    
    # 如果是AJAX请求，返回JSON响应
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'code': 200, 'message': '评论已删除', 'comment_id': comment_id})
    
    flash('评论已删除', 'success')
    return redirect(url_for('blog.post.detail', post_id=post_id))


def delete_comment_tree(comment):
    """递归删除评论及其所有回复"""
    for reply in comment.replies.all():
        delete_comment_tree(reply)
    db.session.delete(comment)


@post_bp.route('/<int:post_id>/favorite', methods=['GET', 'POST'])
@login_required
def favorite(post_id):
    post = Post.query.filter_by(id=post_id, enable=1).first_or_404()
    current_user.favorite(post)
    
    # 如果是AJAX请求，返回JSON响应
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'code': 200, 'message': '已收藏文章'})
    
    # 否则使用传统方式处理
    flash('已收藏文章', 'success')
    return redirect(request.referrer or url_for('blog.post.detail', post_id=post_id))


@post_bp.route('/<int:post_id>/unfavorite', methods=['GET', 'POST'])
@login_required
def unfavorite(post_id):
    post = Post.query.filter_by(id=post_id, enable=1).first_or_404()
    current_user.unfavorite(post)
    
    # 如果是AJAX请求，返回JSON响应
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'code': 200, 'message': '已取消收藏文章'})
    
    # 否则使用传统方式处理
    flash('已取消收藏文章', 'success')
    return redirect(request.referrer or url_for('blog.post.detail', post_id=post_id))

@post_bp.route('/<int:post_id>/like', methods=['POST'])
@login_required
def like(post_id):
    post = Post.query.filter_by(id=post_id, enable=1).first_or_404()
    current_user.like_post(post)
    
    # 如果是AJAX请求，返回JSON响应
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        like_count = post.get_like_count()
        return jsonify({'code': 200, 'message': '已点赞', 'like_count': like_count})
    
    # 否则使用传统方式处理
    flash('已点赞文章', 'success')
    return redirect(request.referrer or url_for('blog.post.detail', post_id=post_id))

@post_bp.route('/<int:post_id>/unlike', methods=['POST'])
@login_required
def unlike(post_id):
    post = Post.query.filter_by(id=post_id, enable=1).first_or_404()
    current_user.unlike_post(post)
    
    # 如果是AJAX请求，返回JSON响应
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        like_count = post.get_like_count()
        return jsonify({'code': 200, 'message': '已取消点赞', 'like_count': like_count})
    
    # 否则使用传统方式处理
    flash('已取消点赞', 'success')
    return redirect(request.referrer or url_for('blog.post.detail', post_id=post_id))
