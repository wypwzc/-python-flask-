"""
标签模型
与文章为多对多关系，通过 post_tags 关联表连接
"""
from app import db
from datetime import datetime


class Tag(db.Model):
    """文章标签表"""
    __tablename__ = 'tags'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), unique=True, nullable=False, comment='标签名称')
    slug = db.Column(db.String(50), unique=True, nullable=False, comment='URL 友好标识')
    post_count = db.Column(db.Integer, default=0, comment='标签下的文章数量（冗余计数）')
    created_at = db.Column(db.DateTime, default=datetime.now, comment='创建时间')

    # 多对多关联 - 通过 post_tags 关联表
    posts = db.relationship(
        'Post',
        secondary='post_tags',
        back_populates='tags',
        lazy='dynamic'
    )

    def update_post_count(self):
        """更新该标签下的文章数量（仅统计已发布的文章）"""
        self.post_count = self.posts.filter_by(is_published=True).count()
        db.session.commit()

    def __repr__(self):
        return f'<Tag {self.name}>'
