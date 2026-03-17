from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from sqlalchemy import desc

from applications.common import curd
from applications.common.curd import enable_status, disable_status
from applications.common.utils import upload as upload_curd
from applications.common.utils.http import table_api, fail_api, success_api
from applications.common.utils.rights import authorize
from applications.common.utils.validate import str_escape
from applications.extensions import db
from applications.models import Role, Dept
from applications.models import User, AdminLog
from applications.models.blog_posts import Post, Comment

bp = Blueprint('user', __name__, url_prefix='/user')


# 用户管理
@bp.get('/')
@authorize("system:user:main")
def main():
    return render_template('system/user/main.html')


#   用户分页查询
@bp.get('/data')
@authorize("system:user:main")
def data():
    # 获取请求参数
    real_name = str_escape(request.args.get('realname', type=str))

    username = str_escape(request.args.get('username', type=str))
    dept_id = request.args.get('deptId', type=int)

    filters = []
    if real_name:
        filters.append(User.realname.contains(real_name))
    if username:
        filters.append(User.username.contains(username))
    if dept_id:
        filters.append(User.dept_id == dept_id)

    # print(*filters)
    query = db.session.query(
        User
    ).filter(*filters).layui_paginate()

    return table_api(
        data=[{
            'id': user.id,
            'username': user.username,
            'realname': user.realname,
            'enable': user.enable,
            'create_at': user.create_at,
            'update_at': user.update_at,
            'dept_name': user.dept_id
        } for user in query.items],
        count=query.total)

    # 用户增加


@bp.get('/add')
@authorize("system:user:add", log=True)
def add():
    roles = Role.query.all()
    return render_template('system/user/add.html', roles=roles)


@bp.post('/save')
@authorize("system:user:add", log=True)
def save():
    req_json = request.get_json(force=True)
    a = req_json.get("roleIds")
    username = str_escape(req_json.get('username'))
    real_name = str_escape(req_json.get('realName'))
    password = str_escape(req_json.get('password'))
    dept_id = str_escape(req_json.get('deptId'))
    role_ids = a.split(',')

    if not username or not real_name or not password:
        return fail_api(msg="账号姓名密码不得为空")

    if bool(User.query.filter_by(username=username).count()):
        return fail_api(msg="用户已经存在")
    user = User(username=username, realname=real_name, enable=1, dept_id=dept_id)
    user.set_password(password)
    db.session.add(user)
    roles = Role.query.filter(Role.id.in_(role_ids)).all()
    for r in roles:
        user.role.append(r)
    db.session.commit()
    return success_api(msg="增加成功")


# 删除用户
@bp.delete('/remove/<int:id>')
@authorize("system:user:remove", log=True)
def delete(id):
    user = User.query.filter_by(id=id).first()
    user.role = []

    res = User.query.filter_by(id=id).delete()
    db.session.commit()
    if not res:
        return fail_api(msg="删除失败")
    return success_api(msg="删除成功")


#  编辑用户
@bp.get('/edit/<int:id>')
@authorize("system:user:edit", log=True)
def edit(id):
    user = curd.get_one_by_id(User, id)
    roles = Role.query.all()
    checked_roles = []
    for r in user.role:
        checked_roles.append(r.id)
    return render_template('system/user/edit.html', user=user, roles=roles, checked_roles=checked_roles)


#  编辑用户
@bp.put('/update')
@authorize("system:user:edit", log=True)
def update():
    try:
        req_json = request.get_json(force=True)
        a = req_json.get("roleIds")
        id = req_json.get("userId")
        if not id:
            return fail_api(msg="用户ID不能为空")
        try:
            id = int(id)
        except ValueError:
            return fail_api(msg="用户ID必须是数字")
        username = str_escape(req_json.get('username'))
        real_name = str_escape(req_json.get('realName'))
        dept_id = req_json.get('deptId')  # 不转换None为字符串
        dept_id = int(dept_id) if dept_id and dept_id.isdigit() else None  # 确保是整数
            
        # 更新基本信息
        User.query.filter_by(id=id).update({'username': username, 'realname': real_name, 'dept_id': dept_id})
        
        # 更新角色信息
        u = User.query.filter_by(id=id).first()
        if not u:
            db.session.rollback()
            return fail_api(msg="用户不存在")
            
        role_ids = a.split(',') if a else []
        roles = Role.query.filter(Role.id.in_(role_ids)).all()
        u.role = roles

        db.session.commit()
        return success_api(msg="更新成功")
    except Exception as e:
        db.session.rollback()
        return fail_api(msg=f"更新失败：{str(e)}")


# 个人中心
@bp.get('/center')
@login_required
def center():
    user_info = current_user
    user_logs = AdminLog.query.filter_by(url='/passport/login').filter_by(uid=current_user.id).order_by(
        desc(AdminLog.create_time)).limit(10)

    blog_count = Post.query.filter_by(user_id=current_user.id).count()  # 发布的博客数量
    my_comments_count = Comment.query.filter_by(user_id=current_user.id).count()  # 我的评论数量
    received_comments_count = Comment.query.join(Post, Comment.post_id == Post.id).filter(Post.user_id == current_user.id).count()  # 收到的评论数量
    recent_posts = (
        Post.query.filter_by(user_id=current_user.id)
        .order_by(desc(Post.create_time))
        .limit(5)
        .all()
    )
    
    # 获取关注的人
    try:
        followed_users = current_user.followed_users().limit(10).all()
    except Exception as e:
        followed_users = []
    
    # 获取收藏的文章
    try:
        favorite_posts = current_user.favorite_posts().limit(10).all()
    except Exception as e:
        favorite_posts = []

    return render_template('system/user/center.html',
                           user_info=user_info,
                           user_logs=user_logs,
                           blog_count=blog_count,
                           my_comments_count=my_comments_count,
                           received_comments_count=received_comments_count,
                           recent_posts=recent_posts,
                           followed_users=followed_users,
                           favorite_posts=favorite_posts
                           )

# 我的收藏
@bp.get('/favorites')
@login_required
def favorites():
    user_info = current_user
    # 获取收藏的文章，使用分页
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    try:
        favorite_posts = current_user.favorite_posts().paginate(page=page, per_page=per_page, error_out=False)
    except Exception as e:
        favorite_posts = None

    return render_template('system/user/favorites.html',
                           user_info=user_info,
                           favorite_posts=favorite_posts.items if favorite_posts else [],
                           pagination=favorite_posts
                           )


# 修改头像
@bp.get('/profile')
@login_required
def profile():
    return render_template('system/user/profile.html')


# 修改头像
@bp.put('/updateAvatar')
@login_required
def update_avatar():
    url = request.get_json(force=True).get("avatar").get("src")
    r = User.query.filter_by(id=current_user.id).update({"avatar": url})
    db.session.commit()
    if not r:
        return fail_api(msg="出错啦")
    return success_api(msg="修改成功")


# 头像上传接口
@bp.post('/uploadAvatar')
@login_required
def upload_avatar():
    if 'file' in request.files:
        photo = request.files['file']
        mime = request.files['file'].content_type
        
        # 限制文件类型
        allowed_extensions = {'jpg', 'jpeg', 'png', 'gif'}
        if '.' in photo.filename and photo.filename.rsplit('.', 1)[1].lower() not in allowed_extensions:
            return jsonify(success=False, msg="仅支持 jpg/jpeg/png/gif 格式的图片")
        
        # 限制文件大小
        if photo.content_length > 5 * 1024 * 1024:  # 5MB
            return jsonify(success=False, msg="图片大小不能超过 5MB")
        
        file_url = upload_curd.upload_one(photo=photo, mime=mime)
        res = {
            "msg": "上传成功",
            "code": 0,
            "success": True,
            "data":
                {"src": file_url}
        }
        return jsonify(res)
    return jsonify(success=False, msg="上传失败")


# 修改当前用户信息
@bp.put('/updateInfo')
@login_required
def update_info():
    req_json = request.get_json(force=True)
    r = User.query.filter_by(id=current_user.id).update(
        {"realname": req_json.get("realName"), "remark": req_json.get("details")})
    db.session.commit()
    if not r:
        return fail_api(msg="出错啦")
    return success_api(msg="更新成功")


# 修改当前用户密码
@bp.get('/editPassword')
@login_required
def edit_password():
    return render_template('system/user/edit_password.html')


# 修改当前用户密码
@bp.put('/editPassword')
@login_required
def edit_password_put():
    res_json = request.get_json(force=True)
    if res_json.get("newPassword") == '':
        return fail_api("新密码不得为空")
    if res_json.get("newPassword") != res_json.get("confirmPassword"):
        return fail_api("俩次密码不一样")
    user = current_user
    is_right = user.validate_password(res_json.get("oldPassword"))
    if not is_right:
        return fail_api("旧密码错误")
    user.set_password(res_json.get("newPassword"))
    db.session.add(user)
    db.session.commit()
    return success_api("更改成功")


# 启用用户
@bp.put('/enable')
@authorize("system:user:edit", log=True)
def enable():
    _id = request.get_json(force=True).get('userId')
    if _id:
        res = enable_status(model=User, id=_id)
        if not res:
            return fail_api(msg="出错啦")
        return success_api(msg="启动成功")
    return fail_api(msg="数据错误")


# 禁用用户
@bp.put('/disable')
@authorize("system:user:edit", log=True)
def dis_enable():
    _id = request.get_json(force=True).get('userId')
    if _id:
        res = disable_status(model=User, id=_id)
        if not res:
            return fail_api(msg="出错啦")
        return success_api(msg="禁用成功")
    return fail_api(msg="数据错误")
