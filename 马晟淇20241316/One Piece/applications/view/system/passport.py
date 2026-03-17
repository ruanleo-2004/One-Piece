import datetime

from flask import Blueprint, session, redirect, url_for, render_template, request, jsonify
from flask_login import current_user, login_user, login_required, logout_user

from applications.common import admin as index_curd
from applications.common.admin_log import login_log
from applications.common.utils.http import fail_api, success_api
from applications.models.admin_user import User, db
from applications.models import Role  # 导入Role模型

bp = Blueprint('passport', __name__, url_prefix='/passport')


# 获取验证码
@bp.get('/getCaptcha')
def get_captcha():
    resp, code = index_curd.get_captcha()
    session["code"] = code
    return resp


# 登录
@bp.get('/login')
def login():
    # 获取参数from
    url_from = request.args.get('url_from') or "home"
    if url_from == 'home':
        target_url = url_for('index.home')
        title = "用户登录"
    elif url_from == 'admin':
        target_url = url_for('index.admin')
        title = "管理员登录"
    else:
        target_url = url_for('index.home')
        title = "用户登录"
    if current_user.is_authenticated:
        return redirect(target_url)
    return render_template('system/login.html', url_from=url_from)


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('system/register.html')

    # 获取表单数据
    data = request.form
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    confirm_password = data.get('confirm_password', '').strip()
    captcha = data.get('captcha', '').strip()

    # 输入验证
    if not username or not password or not confirm_password:
        return jsonify({'success': False, 'msg': '用户名和密码不能为空'})
    if password != confirm_password:
        return jsonify({'success': False, 'msg': '两次输入的密码不一致'})
    # 可添加验证码验证逻辑
    # if not validate_captcha(captcha):
    #     return jsonify({'success': False, 'msg': '验证码错误'})

    # 检查用户名是否已存在
    if User.query.filter_by(username=username).first():
        return jsonify({'success': False, 'msg': '用户名已存在'})

    # 创建用户
    new_user = User(username=username, enable=1)
    new_user.set_password(password)  # 设置密码哈希
    new_user.create_at = datetime.datetime.now()
    new_user.update_at = datetime.datetime.now()
    
    # 为新用户分配普通用户角色（id=2）
    common_role = Role.query.filter_by(id=2).first()
    if common_role:
        new_user.role.append(common_role)
    
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'success': True, 'msg': '注册成功！'})


# 登录
@bp.post('/login')
def login_post():
    req = request.form
    username = req.get('username')
    password = req.get('password')
    remember = bool(req.get('remember-me'))
    code = req.get('captcha').__str__().lower()

    if not username or not password or not code:
        return fail_api(msg="用户名或密码没有输入")
    s_code = session.get("code", None)
    session["code"] = None

    if not all([code, s_code]):
        return fail_api(msg="参数错误")

    if code != s_code:
        return fail_api(msg="验证码错误")
    user = User.query.filter_by(username=username).first()

    if not user:
        return fail_api(msg="不存在的用户")

    if user.enable == 0:
        return fail_api(msg="用户被暂停使用")

    if username == user.username and user.validate_password(password):
        # 登录
        login_user(user, remember=remember)
        # 记录登录日志
        login_log(request, uid=user.id, is_access=True)
        # 授权路由存入session
        role = current_user.role
        user_power = []
        for i in role:
            if i.enable == 0:
                continue
            for p in i.power:
                if p.enable == 0:
                    continue
                user_power.append(p.code)
        session['permissions'] = user_power
        # # 角色存入session
        # roles = []
        # for role in current_user.role.all():
        #     roles.append(role.id)
        # session['role'] = [roles]

        return success_api(msg="登录成功")
    login_log(request, uid=user.id, is_access=False)
    return fail_api(msg="用户名或密码错误")


# 退出登录
@bp.post('/logout')
@login_required
def logout():
    logout_user()
    session.pop('permissions')
    return success_api(msg="注销成功")
