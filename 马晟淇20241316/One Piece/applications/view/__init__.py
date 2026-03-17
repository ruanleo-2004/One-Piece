from applications.view.plugin import register_plugin_views
from applications.view.system import register_system_bps


# from applications.view.blog import register_blog_views

def init_bps(app):
    register_system_bps(app)
    register_plugin_views(app)
