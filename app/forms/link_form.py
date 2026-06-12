"""
友情链接表单
"""
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Optional, URL, NumberRange


class LinkForm(FlaskForm):
    """友情链接表单"""
    name = StringField(
        '站点名称',
        validators=[DataRequired(message='请输入站点名称'), Length(1, 50)],
        render_kw={'placeholder': '如: 张三的博客'}
    )
    url = StringField(
        '站点地址',
        validators=[DataRequired(message='请输入站点地址'), URL(message='请输入正确的 URL'), Length(1, 200)],
        render_kw={'placeholder': '如: https://example.com'}
    )
    description = StringField(
        '描述',
        validators=[Optional(), Length(0, 200)],
        render_kw={'placeholder': '站点描述（可选）'}
    )
    logo = StringField(
        'Logo 地址',
        validators=[Optional(), Length(0, 255)],
        render_kw={'placeholder': 'Logo 图片 URL（可选）'}
    )
    sort_order = IntegerField(
        '排序',
        validators=[NumberRange(min=0, message='排序值必须大于等于 0')],
        default=0,
        render_kw={'placeholder': '0'}
    )
    is_active = BooleanField('启用', default=True)
    submit = SubmitField('保存')
