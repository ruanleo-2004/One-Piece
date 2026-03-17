from flask import Blueprint, request, render_template
from applications.common.utils.http import table_api, success_api, fail_api
from applications.common.utils.rights import authorize
from applications.extensions import db
from applications.models import Comment, Post, User

bp = Blueprint('comment', __name__, url_prefix='/comment')


# 评论管理首页
@bp.get('/')
@authorize("system:comment:main")
def main():
    return render_template('system/comment/main.html')


# 评论分页查询
@bp.get('/data')
@authorize("system:comment:main")
def data():
    content = request.args.get('content', type=str)
    username = request.args.get('username', type=str)
    post_title = request.args.get('post_title', type=str)

    filters = []
    if content:
        filters.append(Comment.content.contains(content))
    if username:
        filters.append(User.username.contains(username))
    if post_title:
        filters.append(Post.title.contains(post_title))

    query  = db.session.query(
        Comment.id,
        Comment.content,
        Comment.date_posted,
        User.username.label('author'),
        Post.title.label('post_title')
    ).filter(*filters).join(User, Comment.user_id == User.id).join(Post, Comment.post_id == Post.id).layui_paginate()

    return table_api(
        data=[ {
            'id': comment.id,
            'content': comment.content,
            'date_posted': comment.date_posted.strftime('%Y-%m-%d %H:%M:%S'),
            'author': comment.author,
            'post_title': comment.post_title
        } for comment in query.items],
        count=query.total
    )


# 添加评论页面
@bp.get('/add')
@authorize("blog:comment:add")
def add():
    posts = Post.query.all()
    users = User.query.all()
    return render_template('system/comment/add.html', posts=posts, users=users)


# 保存新评论
@bp.post('/save')
@authorize("blog:comment:add")
def save():
    req_json = request.get_json(force=True)
    content = req_json.get('content')
    user_id = req_json.get('userId')
    post_id = req_json.get('postId')

    if not content or not user_id or not post_id:
        return fail_api(msg="评论内容、用户ID和文章ID不得为空")

    comment = Comment(content=content, user_id=user_id, post_id=post_id)
    db.session.add(comment)
    db.session.commit()
    return success_api(msg="评论添加成功")


# 编辑评论页面
@bp.get('/edit/<int:id>')
@authorize("blog:comment:edit")
def edit(id):
    comment = Comment.query.get_or_404(id)
    posts = Post.query.all()
    users = User.query.all()
    return render_template('system/comment/edit.html', comment=comment, posts=posts, users=users)


# 更新评论
@bp.put('/update')
@authorize("blog:comment:edit")
def update():
    req_json = request.get_json(force=True)
    comment_id = req_json.get('commentId')
    content = req_json.get('content')
    user_id = req_json.get('userId')
    post_id = req_json.get('postId')

    comment = Comment.query.get_or_404(comment_id)
    comment.content = content
    comment.user_id = user_id
    comment.post_id = post_id

    db.session.commit()
    return success_api(msg="评论更新成功")


# 删除评论
@bp.delete('/remove/<int:id>')
@authorize("blog:comment:remove")
def delete(id):
    comment = Comment.query.get_or_404(id)
    db.session.delete(comment)
    db.session.commit()
    return success_api(msg="评论删除成功")
