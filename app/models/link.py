"""
友情链接模型
支持排序、启用/禁用、Logo 展示
"""
from app import db
from datetime import datetime


class Link(db.Model):
    """友情链接表"""
    __tablename__ = 'links'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False, comment='站点名称')
    url = db.Column(db.String(200), nullable=False, comment='站点 URL')
    description = db.Column(db.String(200), comment='站点描述')
    logo = db.Column(db.String(255), comment='Logo 图片路径')
    sort_order = db.Column(db.Integer, default=0, comment='排序权重（越小越靠前）')
    is_active = db.Column(db.Boolean, default=True, comment='是否启用')
    created_at = db.Column(db.DateTime, default=datetime.now, comment='创建时间')

    def __repr__(self):
        return f'<Link {self.name}>'
