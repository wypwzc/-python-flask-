"""
配置文件 - 支持开发/生产环境切换
使用 python-dotenv 加载 .env 文件中的敏感配置
"""
import os
from dotenv import load_dotenv

# 加载 .env 文件中的环境变量
load_dotenv()


class Config:
    """基础配置"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # 数据库配置
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'mysql+pymysql://root:password@localhost:3306/blog_db')

    # 文件上传配置
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 最大上传 5MB
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'app', 'static', 'uploads')

    # 邮件配置
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'True').lower() in ('true', '1', 'yes')
    MAIL_USERNAME = os.getenv('MAIL_USERNAME', '')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD', '')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_USERNAME', '')

    # 管理员邮箱
    ADMIN_EMAIL = os.getenv('ADMIN_EMAIL', 'admin@example.com')

    # 分页配置
    POSTS_PER_PAGE = 10
    COMMENTS_PER_PAGE = 20

    # Flask-Login 配置
    REMEMBER_COOKIE_DURATION = 7 * 24 * 3600  # 记住登录状态 7 天
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'


class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True


class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False

    # 生产环境需要设置更安全的配置
    SESSION_COOKIE_SECURE = True


class TestingConfig(Config):
    """测试环境配置"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


# 配置映射字典
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
