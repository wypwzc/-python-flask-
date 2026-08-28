"""
自定义装饰器
包含管理员权限验证、请求限制等功能
"""
from functools import wraps
from flask import abort, request, session, jsonify
from flask_login import current_user
import re


def admin_required(f):
    """
    管理员权限验证装饰器
    用于保护后台管理路由，未登录返回 401，非管理员返回 403（JSON）
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return jsonify({'success': False, 'message': '请先登录'}), 401
        if not current_user.is_admin:
            return jsonify({'success': False, 'message': '没有权限访问'}), 403
        return f(*args, **kwargs)
    return decorated_function


def ajax_required(f):
    """
    AJAX 请求验证装饰器
    确保请求是通过 AJAX 发起的
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'error': '非法请求'}), 400
        return f(*args, **kwargs)
    return decorated_function


def rate_limit(max_per_minute=60):
    """
    请求频率限制装饰器（基于 IP + Session）
    用于防止暴力破解和刷接口

    :param max_per_minute: 每分钟最大请求次数
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # 使用 IP + 路由作为限制 key
            ip = request.remote_addr or 'unknown'
            route = request.endpoint or 'unknown'
            key = f'rate_limit:{ip}:{route}'

            # 获取当前请求计数
            count = session.get(key, 0)
            if count >= max_per_minute:
                return jsonify({'error': '请求过于频繁，请稍后再试'}), 429

            # 增加计数并设置过期（通过 session 生命周期）
            session[key] = count + 1
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def comment_rate_limit(f):
    """
    评论提交频率限制装饰器
    限制同一 IP 60 秒内只能评论一次，超限返回 429 JSON
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        ip = request.remote_addr or 'unknown'
        last_comment_time = session.get(f'last_comment_time_{ip}', 0)

        import time
        current_time = time.time()
        if current_time - last_comment_time < 60:
            return jsonify({'success': False, 'message': '评论过于频繁，请 60 秒后再试'}), 429
        # 记录本次评论时间
        session[f'last_comment_time_{ip}'] = current_time
        return f(*args, **kwargs)
    return decorated_function


def sensitive_words_filter(f):
    """
    敏感词过滤装饰器
    检查评论/留言内容是否包含敏感词
    """
    # 敏感词列表（可按需扩展）
    SENSITIVE_WORDS = [
        'spam', 'porn', 'advertisement',
        # 可以添加更多敏感词
    ]

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.method == 'POST':
            # 兼容表单提交与 JSON body
            if request.is_json:
                content = (request.get_json(silent=True) or {}).get('content', '')
            else:
                content = request.form.get('content', '')
            content_lower = content.lower()
            for word in SENSITIVE_WORDS:
                if word in content_lower:
                    return jsonify({'success': False, 'message': '内容包含不当词汇，请修改'}), 400
        return f(*args, **kwargs)
    return decorated_function
