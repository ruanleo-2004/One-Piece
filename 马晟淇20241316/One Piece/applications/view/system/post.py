from flask import Blueprint, render_template, request
from flask_login import current_user, login_required

from applications.common.utils.http import table_api, success_api, fail_api
from applications.common.utils.rights import authorize
from applications.extensions import db
from applications.models import Post, User

bp = Blueprint('post', __name__, url_prefix='/post')


# 博客文章管理
@bp.get('/')
@login_required
@authorize("blog:post:main")
def main():
    return render_template('system/post/main.html')


# 博客文章分页查询
@bp.get('/data')
@login_required
@authorize("blog:post:main")
def data():
    title = request.args.get('title', type=str)
    author_name = request.args.get('author', type=str)

    filters = []
    if title:
        filters.append(Post.title.contains(title))
    if author_name:
        filters.append(User.username.contains(author_name))

    query = db.session.query(
        Post,
        User
    ).filter(*filters).join(User, Post.user_id == User.id).layui_paginate()

    return table_api(
        data=[{
            'id': post.id,
            'title': post.title,
            'content': post.content[:50] + '...' if post.content else '',
            'date_posted': post.date_posted,
            'author': user.username
        } for post, user in query.items],
        count=query.total
    )


# 添加文章页面
@bp.get('/add')
@login_required
@authorize("blog:post:add")
def add():
    users = User.query.all()
    return render_template('system/post/add.html', users=users)


# 保存新文章
@bp.post('/save')
@login_required
@authorize("blog:post:add")
def save():
    req_form = request.form
    title = req_form.get('title')
    content = req_form.get('article')
    user_id = current_user.id  # 获取当前登录用户的 ID
    if not title or not content or not user_id:
        return fail_api(msg="标题、内容和作者不得为空")

    post = Post(title=title, content=content, user_id=user_id)
    db.session.add(post)
    db.session.commit()
    return success_api(msg="文章添加成功")


# 编辑文章页面
@bp.get('/edit/<int:id>')
@login_required
@authorize("blog:post:edit")
def edit(id):
    post = Post.query.get_or_404(id)
    users = User.query.all()
    return render_template('system/post/edit.html', post=post, users=users)


# 更新文章
@bp.put('/update')
@login_required
@authorize("blog:post:edit")
def update():
    post_id = request.args.get('id')
    req_form = request.form
    # post_id = req_form.get('postId')
    title = req_form.get('title')
    content = req_form.get('article')

    post = Post.query.get_or_404(post_id)
    post.title = title
    post.content = content

    db.session.commit()
    return success_api(msg="文章更新成功")


# 删除文章
@bp.delete('/remove/<int:id>')
@login_required
@authorize("blog:post:remove")
def delete(id):
    post = Post.query.get_or_404(id)
    db.session.delete(post)
    db.session.commit()
    return success_api(msg="文章删除成功")
