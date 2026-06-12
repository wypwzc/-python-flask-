"""
文章模型 - 博客核心数据模型
支持 Markdown 渲染、阅读量统计、置顶、多对多标签关联
"""
from app import db
from datetime import datetime


class Post(db.Model):
    """文章表"""
    __tablename__ = 'posts'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(200), nullable=False, comment='文章标题')
    slug = db.Column(db.String(200), unique=True, nullable=False, comment='SEO 友好 URL')
    summary = db.Column(db.String(500), comment='文章摘要')
    content = db.Column(db.Text, nullable=False, comment='Markdown 原始内容')
    content_html = db.Column(db.Text, comment='预渲染的 HTML（缓存）')
    cover_image = db.Column(db.String(255), comment='文章封面图')
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id', ondelete='SET NULL'), comment='所属分类 ID')
    author_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), comment='作者 ID')
    views = db.Column(db.Integer, default=0, comment='阅读量')
    likes = db.Column(db.Integer, default=0, comment='点赞数')
    is_published = db.Column(db.Boolean, default=True, comment='是否发布')
    is_top = db.Column(db.Boolean, default=False, comment='是否置顶')
    allow_comment = db.Column(db.Boolean, default=True, comment='是否允许评论')
    published_at = db.Column(db.DateTime, comment='发布时间')
    created_at = db.Column(db.DateTime, default=datetime.now, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')

    # 关联关系
    tags = db.relationship(
        'Tag',
        secondary='post_tags',
        back_populates='posts',
        lazy='selectin',
        order_by='Tag.name'
    )
    comments = db.relationship(
        'Comment',
        backref='post',
        lazy='dynamic',
        order_by='Comment.created_at.asc()'
    )
    likes_record = db.relationship(
        'PostLike',
        backref='post',
        lazy='dynamic',
        cascade='all, delete-orphan'
    )

    def to_dict(self):
        """转换为字典（用于 API 或模板）"""
        return {
            'id': self.id,
            'title': self.title,
            'slug': self.slug,
            'summary': self.summary,
            'views': self.views,
            'likes': self.likes,
            'is_published': self.is_published,
            'is_top': self.is_top,
            'published_at': self.published_at,
            'created_at': self.created_at,
            'category': self.category.name if self.category else None,
            'tags': [tag.name for tag in self.tags]
        }

    def save_content_html(self):
        """保存渲染后的 HTML（缓存用）"""
        from app.utils.helpers import render_markdown
        self.content_html = render_markdown(self.content)
        db.session.commit()

    def increment_views(self):
        """增加阅读量"""
        self.views = (self.views or 0) + 1
        db.session.commit()

    def __repr__(self):
        return f'<Post {self.title}>'
