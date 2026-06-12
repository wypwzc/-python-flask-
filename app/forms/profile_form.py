"""
个人资料表单
包含基本信息编辑和密码修改
"""
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileSize
from wtforms import StringField, TextAreaField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, Email, Optional, EqualTo


class ProfileForm(FlaskForm):
    """个人资料编辑表单"""
    nickname = StringField(
        '昵称',
        validators=[Optional(), Length(0, 50)],
        render_kw={'placeholder': '显示昵称'}
    )
    email = StringField(
        '邮箱',
        validators=[DataRequired(message='请输入邮箱'), Email(message='邮箱格式不正确')]
    )
    bio = TextAreaField(
        '个人简介',
        validators=[Optional(), Length(0, 500)],
        render_kw={'placeholder': '介绍一下自己...', 'rows': 5}
    )
    avatar = FileField(
        '头像',
        validators=[
            FileAllowed(['jpg', 'jpeg', 'png', 'gif'], '仅支持图片文件'),
            FileSize(max_size=500 * 1024, message='头像大小不能超过 500KB')
        ]
    )
    submit = SubmitField('保存')

    # 密码修改
    old_password = PasswordField('当前密码', validators=[Optional()])
    new_password = PasswordField(
        '新密码',
        validators=[
            Optional(),
            Length(6, 128, message='密码长度至少 6 位'),
            EqualTo('confirm_password', message='两次密码输入不一致')
        ]
    )
    confirm_password = PasswordField('确认新密码', validators=[Optional()])
    change_password = SubmitField('修改密码')
