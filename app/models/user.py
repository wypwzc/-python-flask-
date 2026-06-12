"""
用户模型 - 博客管理员
使用 werkzeug.security 进行密码加密存储
"""
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from datetime import datetime


class User(UserMixin, db.Model):
    """
    用户表 - 仅管理员使用
    继承 UserMixin 获取 Flask-Login 所需的方法（is_authenticated, is_active 等）
    """
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True, nullable=False, comment='用户名')
    email = db.Column(db.String(100), unique=True, nullable=False, comment='电子邮箱')
    password_hash = db.Column(db.String(255), nullable=False, comment='密码哈希值（werkzeug 加密）')
    avatar = db.Column(db.String(255), comment='头像图片路径')
    nickname = db.Column(db.String(50), comment='显示昵称')
    bio = db.Column(db.Text, comment='个人简介')
    is_admin = db.Column(db.Boolean, default=True, comment='是否为管理员')
    login_ip = db.Column(db.String(45), comment='最近登录 IP')
    last_login = db.Column(db.DateTime, comment='最近登录时间')
    created_at = db.Column(db.DateTime, default=datetime.now, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')

    # 关联关系
    posts = db.relationship('Post', backref='author', lazy='dynamic')

    def set_password(self, password):
        """
        设置密码 - 加密存储
        使用 pbkdf2:sha256 算法，自动生成盐值
        """
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')

    def check_password(self, password):
        """
        验证密码
        :return: True/False
        """
        return check_password_hash(self.password_hash, password)

    @property
    def display_name(self):
        """获取展示名称（优先使用昵称）"""
        return self.nickname or self.username

    def __repr__(self):
        return f'<User {self.username}>'
