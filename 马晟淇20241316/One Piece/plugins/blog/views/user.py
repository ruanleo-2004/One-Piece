from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from applications.models.admin_user import User
from applications.models.blog_posts import Post
from applications.extensions import db

# 创建用户蓝图
user_bp = Blueprint('user', __name__)

@user_bp.route('/<int:user_id>')
def profile(user_id):    
    # 获取用户信息
    user = User.query.get_or_404(user_id)
    
    # 获取用户发布的所有文章
    page = request.args.get('page', 1, type=int)
    per_page = 10
    posts = Post.query.filter_by(user_id=user_id).order_by(Post.date_posted.desc()).paginate(page=page, per_page=per_page)
    
    # 渲染用户个人主页模板
    return render_template('user/profile.html', user=user, posts=posts)

@user_bp.route('/follow/<int:user_id>')
@login_required
def follow(user_id):
    user = User.query.get_or_404(user_id)
    if current_user.id == user_id:
        flash('不能关注自己', 'warning')
        return redirect(url_for('blog.user.profile', user_id=user_id))
    
    current_user.follow(user)
    flash(f'已关注 {user.realname}', 'success')
    return redirect(url_for('blog.user.profile', user_id=user_id))

@user_bp.route('/unfollow/<int:user_id>')
@login_required
def unfollow(user_id):
    user = User.query.get_or_404(user_id)
    if current_user.id == user_id:
        flash('不能取消关注自己', 'warning')
        return redirect(url_for('blog.user.profile', user_id=user_id))
    
    current_user.unfollow(user)
    flash(f'已取消关注 {user.realname}', 'success')
    return redirect(url_for('blog.user.profile', user_id=user_id))

@user_bp.route('/favorites')
@login_required
def favorites():
    # 获取当前用户收藏的所有文章
    page = request.args.get('page', 1, type=int)
    per_page = 10
    favorite_posts = current_user.favorite_posts().order_by(Post.date_posted.desc()).paginate(page=page, per_page=per_page)
    
    # 渲染收藏页面模板
    return render_template('user/favorites.html', favorite_posts=favorite_posts)
