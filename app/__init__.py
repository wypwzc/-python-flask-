"""
Flask 应用工厂
使用 create_app() 函数创建应用实例，支持不同环境配置
"""
from datetime import datetime
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from flask_wtf import CSRFProtect
from config import config

# 初始化扩展（延迟初始化，在 create_app 中绑定到 app）
db = SQLAlchemy()
login_manager = LoginManager()
mail = Mail()
csrf = CSRFProtect()


def create_app(config_name='development'):
    """
    应用工厂函数
    :param config_name: 配置名称（development/production/testing）
    :return: Flask 应用实例
    """
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # 初始化扩展
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    csrf.init_app(app)

    # 配置 Flask-Login
    login_manager.login_view = 'auth.login'
    login_manager.login_message = '请先登录后再访问后台管理'
    login_manager.login_message_category = 'warning'

    # 注册蓝图
    from app.views.front import front_bp
    from app.views.admin import admin_bp
    from app.views.auth import auth_bp

    app.register_blueprint(front_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(auth_bp, url_prefix='/auth')

    # 注册模板上下文处理器
    @app.context_processor
    def inject_global_data():
        """注入全局模板变量"""
        from app.models.category import Category
        from app.models.post import Post
        from app.models.comment import Comment
        from app.models.site_stats import SiteStats
        from app.models.user import User
        from flask_wtf.csrf import generate_csrf

        categories = Category.query.order_by(Category.post_count.desc()).all()
        recent_posts = Post.query.filter_by(is_published=True)\
            .order_by(Post.published_at.desc()).limit(5).all()
        recent_comments = Comment.query.filter_by(is_approved=True)\
            .order_by(Comment.created_at.desc()).limit(5).all()
        total_stats = SiteStats.get_total_stats()
        blog_admin = User.query.filter_by(is_admin=True).first()
        return {
            'categories': categories,
            'recent_posts': recent_posts,
            'recent_comments': recent_comments,
            'total_stats': total_stats,
            'blog_admin': blog_admin,
            'now': datetime.now,
            'csrf_token': generate_csrf
        }

    # 注册错误处理器
    @app.errorhandler(404)
    def not_found_error(error):
        """404 页面"""
        return render_template('front/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        """500 页面"""
        db.session.rollback()
        return render_template('front/500.html'), 500

    # 注册模板过滤器
    from app.utils.helpers import (
        format_datetime, truncate_text, render_markdown,
        time_ago, count_words, calculate_reading_time
    )
    app.add_template_filter(format_datetime, 'format_datetime')
    app.add_template_filter(truncate_text, 'truncate')
    app.add_template_filter(render_markdown, 'markdown')
    app.add_template_filter(time_ago, 'time_ago')
    app.add_template_filter(count_words, 'word_count')
    app.add_template_filter(calculate_reading_time, 'reading_time')

    return app


# 用户加载回调 - Flask-Login 使用
from app.models.user import User


@login_manager.user_loader
def load_user(user_id):
    """根据用户ID从数据库加载用户对象"""
    return User.query.get(int(user_id))
