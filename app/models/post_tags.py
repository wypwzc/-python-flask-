"""
文章-标签关联表（多对多关系）
手动定义关联表以支持更灵活的操作
"""
from app import db


# 文章与标签的多对多关联表
post_tags = db.Table('post_tags',
    db.Column('post_id', db.Integer, db.ForeignKey('posts.id', ondelete='CASCADE'),
              primary_key=True, comment='文章 ID'),
    db.Column('tag_id', db.Integer, db.ForeignKey('tags.id', ondelete='CASCADE'),
              primary_key=True, comment='标签 ID')
)
