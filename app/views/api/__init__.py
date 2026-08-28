"""
REST API 蓝图 - 供 Vue 3 前端 SPA 消费
- front: 前台数据接口（文章/分类/标签/归档/搜索/留言等）
- auth: 认证接口（登录/登出/当前用户）
- admin: 后台管理接口（文章/分类/标签/友链/评论/个人资料）
"""
from flask import Blueprint

api_bp = Blueprint('api', __name__, url_prefix='/api')

# 注册子模块（延迟导入避免循环引用）
from app.views.api import front, auth, admin  # noqa: E402,F401
