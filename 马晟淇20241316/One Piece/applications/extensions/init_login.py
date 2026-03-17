from flask_login import LoginManager
from flask import jsonify, request


def init_login_manager(app):
    login_manager = LoginManager()
    login_manager.init_app(app)

    login_manager.login_view = 'system.passport.login'

    @login_manager.user_loader
    def load_user(user_id):
        from applications.models import User
        user = User.query.get(int(user_id))
        return user
        
    @login_manager.unauthorized_handler
    def unauthorized():
        # 如果是AJAX请求，返回JSON错误响应
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'code': 401, 'message': '请先到个人中心登录'})
        # 否则重定向到登录页面
        return login_manager.unauthorized_callback()
