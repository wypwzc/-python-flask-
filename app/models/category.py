"""
分类模型
使用 slug 作为 URL 友好标识，post_count 为冗余计数优化查询
"""
from app import db
from datetime import datetime


class Category(db.Model):
    """文章分类表"""
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), unique=True, nullable=False, comment='分类名称')
    slug = db.Column(db.String(50), unique=True, nullable=False, comment='URL 友好标识')
    description = db.Column(db.String(200), comment='分类描述')
    post_count = db.Column(db.Integer, default=0, comment='文章数量（冗余计数）')
    created_at = db.Column(db.DateTime, default=datetime.now, comment='创建时间')

    # 关联关系
    posts = db.relationship('Post', backref='category', lazy='dynamic')

    def update_post_count(self):
        """更新该分类下的文章数量（仅统计已发布的文章）"""
        from app.models.post import Post
        self.post_count = Post.query.filter_by(
            category_id=self.id, is_published=True
        ).count()
        db.session.commit()

    def __repr__(self):
        return f'<Category {self.name}>'
