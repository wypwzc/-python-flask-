"""
文章/分类/标签表单
支持 Markdown 编辑、标签选择、分类选择等功能
"""
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileSize
from wtforms import StringField, TextAreaField, SelectField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Optional, URL
from app.models.category import Category
from app.models.tag import Tag


class PostForm(FlaskForm):
    """文章新增/编辑表单"""
    title = StringField(
        '文章标题',
        validators=[
            DataRequired(message='请输入文章标题'),
            Length(1, 200, message='标题长度为 1-200 个字符')
        ],
        render_kw={'placeholder': '请输入文章标题'}
    )
    slug = StringField(
        'URL 别名',
        validators=[
            DataRequired(message='请输入 URL 别名'),
            Length(1, 200, message='别名为 1-200 个字符')
        ],
        render_kw={'placeholder': '如: my-first-post（自动生成）'}
    )
    summary = TextAreaField(
        '文章摘要',
        validators=[Length(0, 500, message='摘要不超过 500 个字符')],
        render_kw={'placeholder': '文章摘要（可选，留空自动截取前 150 字）', 'rows': 3}
    )
    content = TextAreaField(
        '文章内容 (Markdown)',
        validators=[DataRequired(message='请输入文章内容')],
        render_kw={'placeholder': '使用 Markdown 语法编写...', 'rows': 20}
    )
    category_id = SelectField('所属分类', coerce=int, validators=[Optional()])
    tags = StringField(
        '标签',
        render_kw={'placeholder': '输入标签名，用逗号分隔'}
    )
    cover_image = FileField(
        '封面图片',
        validators=[
            FileAllowed(['jpg', 'jpeg', 'png', 'gif', 'webp'], '仅支持图片文件（jpg/png/gif/webp）'),
            FileSize(max_size=5 * 1024 * 1024, message='图片大小不能超过 5MB')
        ]
    )
    is_published = BooleanField('发布', default=True)
    is_top = BooleanField('置顶', default=False)
    allow_comment = BooleanField('允许评论', default=True)
    submit = SubmitField('保存')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 动态加载分类选项
        categories = Category.query.order_by(Category.post_count.desc()).all()
        self.category_id.choices = [(0, '未分类')] + [(c.id, c.name) for c in categories]

    def validate_slug(self, field):
        """验证 slug 格式"""
        import re
        if not re.match(r'^[a-z0-9\-]+$', field.data):
            from wtforms import ValidationError
            raise ValidationError('URL 别名只能包含小写字母、数字和短横线')


class CategoryForm(FlaskForm):
    """分类表单"""
    name = StringField(
        '分类名称',
        validators=[
            DataRequired(message='请输入分类名称'),
            Length(1, 50, message='名称为 1-50 个字符')
        ],
        render_kw={'placeholder': '如: 技术笔记'}
    )
    slug = StringField(
        'URL 别名',
        validators=[
            DataRequired(message='请输入 URL 别名'),
            Length(1, 50, message='别名为 1-50 个字符')
        ],
        render_kw={'placeholder': '如: tech-notes'}
    )
    description = StringField(
        '描述',
        validators=[Length(0, 200, message='描述不超过 200 个字符')],
        render_kw={'placeholder': '分类描述（可选）'}
    )
    submit = SubmitField('保存')


class TagForm(FlaskForm):
    """标签表单"""
    name = StringField(
        '标签名称',
        validators=[
            DataRequired(message='请输入标签名称'),
            Length(1, 50, message='名称为 1-50 个字符')
        ],
        render_kw={'placeholder': '如: Python'}
    )
    slug = StringField(
        'URL 别名',
        validators=[
            DataRequired(message='请输入 URL 别名'),
            Length(1, 50, message='别名为 1-50 个字符')
        ],
        render_kw={'placeholder': '如: python'}
    )
    submit = SubmitField('保存')
