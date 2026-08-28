"""
Flask 应用工厂
使用 create_app() 函数创建应用实例，支持不同环境配置
"""
import os
from flask import Flask, request, abort, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from flask_wtf import CSRFProtect
from flask_wtf.csrf import generate_csrf
from config import config

# 初始化扩展（延迟初始化，在 create_app 中绑定到 app）
db = SQLAlchemy()
login_manager = LoginManager()
mail = Mail()
csrf = CSRFProtect()

# Vue 前端构建产物目录（存在时启用 SPA 托管）
DIST_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'frontend', 'dist')


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

    # 配置 Flask-Login（401 由前端拦截器统一跳转登录页）
    login_manager.login_view = None

    # 注册 API 蓝图（前台/后台均为 SPA 调用的 REST 接口）
    from app.views.api import api_bp

    app.register_blueprint(api_bp)

    # ─── Vue 3 SPA 支持 ──────────────────────────────

    # 每个响应下发 CSRF token cookie，前端读取后回传 X-CSRFToken 头
    @app.after_request
    def set_csrf_cookie(response):
        token = generate_csrf()
        response.set_cookie('csrf_token', token, httponly=False, samesite='Lax')
        return response

    # 注册错误处理器（/api 返回 JSON，其余返回 SPA index.html）
    from app.views.api.errors import register_error_handlers
    register_error_handlers(app)

    # 生产模式：托管 Vue 构建产物 + history 路由 fallback
    if os.path.isdir(DIST_DIR):
        @app.route('/', defaults={'path': ''})
        @app.route('/<path:path>')
        def serve_spa(path):
            if path.startswith(('api/', 'static/')):
                abort(404)
            file_path = os.path.join(DIST_DIR, path)
            if path and os.path.isfile(file_path):
                return send_from_directory(DIST_DIR, path)
            return send_from_directory(DIST_DIR, 'index.html')

    return app


# 用户加载回调 - Flask-Login 使用
from app.models.user import User


@login_manager.user_loader
def load_user(user_id):
    """根据用户ID从数据库加载用户对象"""
    return User.query.get(int(user_id))
