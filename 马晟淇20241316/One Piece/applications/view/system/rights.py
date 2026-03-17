import copy
from collections import OrderedDict

from flask import jsonify, Blueprint, request
# 控制台页面
from flask import render_template
from flask import session, current_app
from flask_login import current_user
from flask_login import login_required

from applications.models import Post, Series, NewsArticle, User, Comment,Feedback
from ...models import Power
from ...schemas import PowerOutSchema

bp = Blueprint('rights', __name__, url_prefix='/rights')


# 渲染配置
@bp.get('/configs')
@login_required
def configs():
    # 获取title参数
    # title = request.args.get('title')
    url_from = request.args.get('url_from')
    title = "个人首页" if url_from == "home" else "管理员中心"

    # 网站配置
    def is_manager():
        if current_user.username != current_app.config.get("SUPERADMIN"):
            return bool("system:post:main" in session.get('permissions'))
        else:
            return True

    config = dict(logo={
        # 网站名称
        "title": title if title else "用户中心",
        # 网站图标
        "image": "/static/picture/logo.png"
        # 菜单配置
    }, menu={
        # 菜单数据来源
        "data": "/system/rights/menu?url_from=" + url_from if url_from else "/system/rights/menu",
        "collaspe": False,
        # 是否同时只打开一个菜单目录
        "accordion": True,
        "method": "GET",
        # 是否开启多系统菜单模式
        "control": False,
        # 顶部菜单宽度 PX
        "controlWidth": 500,
        # 默认选中的菜单项
        "select": "0",
        # 是否开启异步菜单，false 时 data 属性设置为菜单数据，false 时为 json 文件或后端接口
        "async": True
    }, tab={
        # 是否开启多选项卡
        "enable": True,
        # 切换选项卡时，是否刷新页面状态
        "keepState": True,
        # 是否开启 Tab 记忆
        "session": True,
        # 最大可打开的选项卡数量
        "max": 30,
        "index": {
            # 标识 ID , 建议与菜单项中的 ID 一致
            "id": "10",
            # 页面地址
            "href": "/system/rights/welcome" if url_from == "admin" else "/system/user/center",
            # 标题
            "title": "首页"
        }
    }, theme={
        # 默认主题色，对应 colors 配置中的 ID 标识
        "defaultColor": "2",
        # 默认的菜单主题 dark-theme 黑 / light-theme 白
        "defaultMenu": "dark-theme",
        # 是否允许用户切换主题，false 时关闭自定义主题面板
        "allowCustom": True
    }, colors=[{
        "id": "1",
        "color": "#2d8cf0"
    },
        {
            "id": "2",
            "color": "#5FB878"
        },
        {
            "id": "3",
            "color": "#1E9FFF"
        }, {
            "id": "4",
            "color": "#FFB800"
        }, {
            "id": "5",
            "color": "darkgray"
        }, {
            "id": "6",
            "color": "#fb7299"
        }
    ], links=current_app.config.get("SYSTEM_PANEL_LINKS"), other={
        # 主页动画时长
        "keepLoad": 0,
        # 布局顶部主题
        "autoHead": False
    }, header=False)
    print(config)
    return jsonify(config)


# 菜单
@bp.get('/menu')
@login_required
def menu():
    url_from = request.args.get('url_from')
    if current_user.username != current_app.config.get("SUPERADMIN") or url_from == "home":
        if url_from == "home":
            powers = []
            role = current_user.role
            for i in role:
                # 如果角色没有被启用就直接跳过
                if i.enable == 0:
                    continue
                # 变量角色用户的权限
                for p in i.power:
                    # 如果权限关闭了就直接跳过
                    if p.enable == 0:
                        continue
                    # 一二级菜单
                    if int(p.type) in [0, 1] and p not in powers:
                        if p.code and p.code.startswith('user'):
                            powers.append(p)

            # powers = [p for p in current_user.powers if p.enable == 1 and p.name.startswith('user')]
        else:
            role = current_user.role
            powers = []
            for i in role:
                # 如果角色没有被启用就直接跳过
                if i.enable == 0:
                    continue
                # 变量角色用户的权限
                for p in i.power:
                    # 如果权限关闭了就直接跳过
                    if p.enable == 0:
                        continue
                    # 一二级菜单
                    if int(p.type) in [0, 1] and p not in powers:
                        powers.append(p)

        power_schema = PowerOutSchema(many=True)  # 用已继承 ma.ModelSchema 类的自定制类生成序列化类
        power_dict = power_schema.dump(powers)  # 生成可序列化对象
        power_dict.sort(key=lambda x: (x['parent_id'], x['id']), reverse=True)
        print(power_dict)
        menu_dict = OrderedDict()
        for _dict in power_dict:
            if _dict['id'] in menu_dict:
                # 当前节点添加子节点
                _dict['children'] = copy.deepcopy(menu_dict[_dict['id']])
                _dict['children'].sort(key=lambda item: item['sort'])
                # 删除子节点
                del menu_dict[_dict['id']]

            if _dict['parent_id'] not in menu_dict:

                menu_dict[_dict['parent_id']] = [_dict]
            else:
                menu_dict[_dict['parent_id']].append(_dict)
        return jsonify(sorted(menu_dict.get(0), key=lambda item: item['sort']))
    else:
        powers = Power.query.filter_by(enable=1).all()
        # print(powers)
        power_schema = PowerOutSchema(many=True)  # 用已继承 ma.ModelSchema 类的自定制类生成序列化类
        power_dict = power_schema.dump(powers)  # 生成可序列化对象
        power_dict.sort(key=lambda x: (x['parent_id'], x['id']), reverse=True)

        menu_dict = OrderedDict()
        for _dict in power_dict:
            if _dict['id'] in menu_dict:
                # 当前节点添加子节点
                _dict['children'] = copy.deepcopy(menu_dict[_dict['id']])
                _dict['children'].sort(key=lambda item: item['sort'])
                # 删除子节点
                del menu_dict[_dict['id']]

            if _dict['parent_id'] not in menu_dict:
                menu_dict[_dict['parent_id']] = [_dict]
            else:
                menu_dict[_dict['parent_id']].append(_dict)
        return jsonify(sorted(menu_dict.get(0), key=lambda item: item['sort']))


@bp.get('/welcome')
@login_required
def welcome():
    # 获取数据的计数
    post_count = Post.query.count()  # 当前推文数量
    series_count = Series.query.count()  # 系列数量
    news_count = NewsArticle.query.count()  # 新闻数量
    user_count = User.query.count()  # 用户数量
    comment_count = Comment.query.count()  # 评论数量
    feedback_list = Feedback.query.all()  # 获取所有反馈

    # 将计数和反馈列表传递给模板
    return render_template(
        'system/console/console.html',
        post_count=post_count,
        series_count=series_count,
        news_count=news_count,
        user_count=user_count,
        comment_count=comment_count,
        feedback_list=feedback_list  # 添加反馈数据
    )
