"""
文章点赞记录模型
基于 IP 地址限制每篇文章每人只能点赞一次
"""
from app import db
from datetime import datetime


class PostLike(db.Model):
    """文章点赞记录表"""
    __tablename__ = 'post_likes'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id', ondelete='CASCADE'),
                        nullable=False, comment='文章 ID')
    ip_address = db.Column(db.String(45), nullable=False, comment='点赞者 IP')
    user_agent = db.Column(db.String(255), comment='浏览器 User-Agent')
    created_at = db.Column(db.DateTime, default=datetime.now, comment='点赞时间')

    # 联合唯一索引：同一 IP 对同一文章只能点赞一次
    __table_args__ = (
        db.UniqueConstraint('post_id', 'ip_address', name='uk_post_ip'),
    )

    def __repr__(self):
        return f'<PostLike post={self.post_id} ip={self.ip_address}>'
