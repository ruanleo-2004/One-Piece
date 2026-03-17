from flask import Blueprint, render_template

# 这个文件不需要单独的蓝图，因为main.py中已经有了blog_blueprint
# 并且已经定义了@blog_blueprint.route("/")来处理根路径
# 这个文件可以删除，或者保留作为备份
