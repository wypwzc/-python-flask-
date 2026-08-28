"""
API 错误处理 - 注册应用级错误处理器
按路径前缀分流：/api 返回 JSON，其余返回 SPA index.html（由 Vue 前端渲染 404/错误页）
"""
import os

from flask import jsonify, request, send_from_directory

DIST_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 'frontend', 'dist')


def _is_api_path():
    return request.path.startswith('/api')


def _is_csrf_error(error):
    """判断是否为 CSRF 校验失败（CSRFError 是 BadRequest 的子类）"""
    from flask_wtf.csrf import CSRFError
    return isinstance(error, CSRFError)


def _json_error(message, code):
    return jsonify({'success': False, 'message': message}), code


def _serve_spa():
    """返回 SPA 入口（dist 存在时），否则返回简单错误页"""
    if os.path.isdir(DIST_DIR):
        return send_from_directory(DIST_DIR, 'index.html')
    return None


def register_error_handlers(app):
    """注册 400/401/403/404/500 错误处理器"""

    @app.errorhandler(401)
    def unauthorized(error):
        """未登录/登录态失效（flask-login login_required 触发）"""
        if _is_api_path():
            return _json_error('请先登录', 401)
        result = _serve_spa()
        return result or ('请先登录', 401)

    @app.errorhandler(400)
    def bad_request(error):
        if _is_api_path():
            if _is_csrf_error(error):
                return _json_error('CSRF 验证失败，请刷新页面后重试', 400)
            return _json_error('请求无效', 400)
        result = _serve_spa()
        return result or ('请求无效', 400)

    @app.errorhandler(403)
    def forbidden(error):
        if _is_api_path():
            return _json_error('没有权限访问', 403)
        result = _serve_spa()
        return result or ('没有权限访问', 403)

    @app.errorhandler(404)
    def not_found(error):
        if _is_api_path():
            return _json_error('资源不存在', 404)
        result = _serve_spa()
        return result or ('页面不存在', 404)

    @app.errorhandler(500)
    def internal_error(error):
        from app import db
        db.session.rollback()
        app.logger.error(f'服务器内部错误: {error}')
        if _is_api_path():
            return _json_error('服务器内部错误', 500)
        result = _serve_spa()
        return result or ('服务器内部错误', 500)
