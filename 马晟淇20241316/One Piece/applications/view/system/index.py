from flask import Blueprint, render_template, redirect
from flask_login import login_required, current_user

bp = Blueprint('index', __name__, url_prefix='/')


# 首页
@bp.get('/admin')
# @login_required
def admin():
    if current_user.is_authenticated:
        return render_template('system/index.html', user=current_user, title='后台管理',
                               url_from='admin')
    else:
        return redirect('/system/passport/login?url_from=admin')
    # return render_template('system/index.html', user=user)


@bp.get('/home')
# @login_required
def home():
    if current_user.is_authenticated:
        return render_template('system/index.html', user=current_user, title='用户中心', url_from="home")
    else:
        return redirect('/system/passport/login?url_from=home')
    # return render_template('system/index.html', user=user)


@bp.get('/')
def index():
    user = current_user
    return redirect('/blog/')
