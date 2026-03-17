from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, SelectField, TextAreaField, BooleanField, FileField
from wtforms.validators import DataRequired, Email, Length
from flask_wtf.file import FileAllowed


class FeedbackForm(FlaskForm):
    name = StringField('姓名', validators=[DataRequired(message='请输入姓名'), Length(min=2, max=20, message='姓名长度必须在2-20个字符之间')])
    email = EmailField('邮箱', validators=[DataRequired(message='请输入邮箱'), Email(message='请输入有效的邮箱地址')])
    phone = StringField('电话')
    category = SelectField(
        '反馈类型', 
        choices=[
            ('general', '一般咨询'),
            ('technical', '技术问题'),
            ('suggestion', '建议'),
            ('complaint', '投诉')
        ],
        validators=[DataRequired(message='请选择反馈类型')]
    )
    message = TextAreaField('反馈内容', validators=[DataRequired(message='请输入反馈内容'), Length(min=10, message='反馈内容至少10个字符')])
    attachment = FileField('附件', validators=[FileAllowed(['jpg', 'jpeg', 'png'], message='仅支持JPG和PNG格式的图片')])
    agree = BooleanField('我已阅读并同意隐私政策', validators=[DataRequired(message='请同意隐私政策')])