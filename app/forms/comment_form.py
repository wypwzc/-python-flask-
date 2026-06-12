"""
评论/留言表单
支持访客评论的表单校验，包含昵称、邮箱、内容等字段
"""
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length, Email, Optional, URL


class CommentForm(FlaskForm):
    """文章评论表单"""
    author_name = StringField(
        '昵称',
        validators=[DataRequired(message='请输入昵称'), Length(1, 50)],
        render_kw={'placeholder': '你的昵称 *'}
    )
    author_email = StringField(
        '邮箱',
        validators=[DataRequired(message='请输入邮箱'), Email(message='邮箱格式不正确'), Length(1, 100)],
        render_kw={'placeholder': '你的邮箱 *（不会公开显示）'}
    )
    author_url = StringField(
        '网站',
        validators=[Optional(), URL(message='网址格式不正确'), Length(0, 200)],
        render_kw={'placeholder': '个人网站（可选）'}
    )
    content = TextAreaField(
        '评论内容',
        validators=[DataRequired(message='请输入评论内容'), Length(1, 2000, message='评论内容为 1-2000 个字符')],
        render_kw={'placeholder': '写下你的评论...', 'rows': 5}
    )
    submit = SubmitField('发表评论')


class MessageForm(FlaskForm):
    """全站留言板表单"""
    author_name = StringField(
        '昵称',
        validators=[DataRequired(message='请输入昵称'), Length(1, 50)],
        render_kw={'placeholder': '你的昵称 *'}
    )
    author_email = StringField(
        '邮箱',
        validators=[DataRequired(message='请输入邮箱'), Email(message='邮箱格式不正确'), Length(1, 100)],
        render_kw={'placeholder': '你的邮箱 *'}
    )
    content = TextAreaField(
        '留言内容',
        validators=[DataRequired(message='请输入留言内容'), Length(1, 2000, message='留言内容为 1-2000 个字符')],
        render_kw={'placeholder': '写下你想说的话...', 'rows': 5}
    )
    submit = SubmitField('发布留言')
