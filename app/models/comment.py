"""
评论/留言模型
支持嵌套回复（最多 2 层），记录 IP 防 spam
post_id 为 NULL 表示全站留言板留言
"""
from app import db
from datetime import datetime


class Comment(db.Model):
    """评论/留言表"""
    __tablename__ = 'comments'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id', ondelete='CASCADE'),
                        nullable=True, comment='关联文章 ID（NULL 表示全站留言）')
    parent_id = db.Column(db.Integer, db.ForeignKey('comments.id', ondelete='CASCADE'),
                          nullable=True, comment='父评论 ID（用于嵌套回复）')
    author_name = db.Column(db.String(50), nullable=False, comment='访客昵称')
    author_email = db.Column(db.String(100), nullable=False, comment='访客邮箱')
    author_url = db.Column(db.String(200), comment='访客个人网站')
    content = db.Column(db.Text, nullable=False, comment='评论内容')
    is_admin = db.Column(db.Boolean, default=False, comment='是否为博主回复')
    ip_address = db.Column(db.String(45), comment='评论者 IP 地址')
    user_agent = db.Column(db.String(255), comment='浏览器 User-Agent')
    is_approved = db.Column(db.Boolean, default=True, comment='审核状态')
    created_at = db.Column(db.DateTime, default=datetime.now, comment='创建时间')

    # 自引用关系（嵌套回复）
    replies = db.relationship(
        'Comment',
        backref=db.backref('parent', remote_side=[id]),
        lazy='dynamic',
        cascade='all, delete-orphan'
    )

    @property
    def is_article_comment(self):
        """是否为文章评论（而非全站留言）"""
        return self.post_id is not None

    def get_replies(self, max_depth=2):
        """获取回复列表（限制嵌套深度）"""
        if max_depth <= 0:
            return []
        replies = Comment.query.filter_by(parent_id=self.id, is_approved=True)\
            .order_by(Comment.created_at.asc()).all()
        for reply in replies:
            reply.nested_replies = reply.get_replies(max_depth - 1)
        return replies

    def __repr__(self):
        return f'<Comment {self.id} by {self.author_name}>'
