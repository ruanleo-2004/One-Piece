from flask import Blueprint, render_template, jsonify, request, redirect, url_for, flash

from applications.common.utils.upload import upload_one
from applications.models.blog_concat import db, Feedback  # 假设你已经定义了Feedback模型
from plugins.blog.forms.feedback import FeedbackForm

about_bp = Blueprint('about', __name__)


@about_bp.route('/')
def index():
    return render_template("about/about.html")


@about_bp.route('/concat', methods=['GET', 'POST'])
def concat():
    form = FeedbackForm()
    
    if request.method == 'POST' and form.validate_on_submit():
        # 获取表单数据
        name = form.name.data
        email = form.email.data
        phone = form.phone.data
        category = form.category.data
        message = form.message.data
        agree = form.agree.data

        # 处理附件上传
        attachment = form.attachment.data
        if attachment:
            # 保存文件到指定目录
            mime = attachment.filename.rsplit('.', 1)[-1].lower()
            file_url = upload_one(photo=attachment, mime=mime)
        else:
            file_url = None  # 未上传附件

        # 创建反馈实例并保存到数据库
        feedback = Feedback(
            name=name,
            email=email,
            phone=phone,
            category=category,
            message=message,
            attachment=file_url,  # 存储文件URL
            agree=agree
        )
        db.session.add(feedback)
        db.session.commit()

        flash('反馈已成功提交！', 'success')
        return redirect(url_for('blog.about.concat'))

    return render_template('about/concat.html', form=form)


@about_bp.route('/terms')
def terms():
    return render_template('about/terms.html')
