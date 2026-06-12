"""
登录表单
使用 Flask-WTF 实现 CSRF 保护 + 表单校验
"""
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length


class LoginForm(FlaskForm):
    """管理员登录表单"""
    username = StringField(
        '用户名',
        validators=[
            DataRequired(message='请输入用户名'),
            Length(1, 50, message='用户名为 1-50 个字符')
        ],
        render_kw={'placeholder': '请输入用户名', 'autofocus': ''}
    )
    password = PasswordField(
        '密码',
        validators=[
            DataRequired(message='请输入密码'),
            Length(1, 255, message='密码为 1-255 个字符')
        ],
        render_kw={'placeholder': '请输入密码'}
    )
    remember_me = BooleanField('记住我', default=False)
    submit = SubmitField('登录')
