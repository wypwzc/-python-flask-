"""
认证 API - 注册/登录/登出/当前用户
保留 Flask-Login session cookie 认证（同源 SPA 直接可用）
"""
import re
from datetime import datetime

from flask import jsonify, request
from flask_login import login_user, logout_user, login_required, current_user

from app import db
from app.models.user import User
from app.utils.helpers import get_client_ip
from app.views.api import api_bp
from app.views.api.serializers import user_to_dict

_EMAIL_RE = re.compile(r'^[^@\s]+@[^@\s]+\.[^@\s]+$')


@api_bp.route('/auth/register', methods=['POST'])
def register():
    """开放注册（普通用户，非管理员），注册成功自动登录"""
    if current_user.is_authenticated:
        return jsonify({'success': True, 'user': user_to_dict(current_user)})

    data = request.get_json(silent=True) or {}
    username = (data.get('username') or '').strip()
    nickname = (data.get('nickname') or '').strip()
    email = (data.get('email') or '').strip()
    password = data.get('password') or ''

    errors = {}
    if not username or len(username) < 3:
        errors['username'] = '用户名至少 3 个字符'
    elif len(username) > 50:
        errors['username'] = '用户名不能超过 50 个字符'
    elif User.query.filter_by(username=username).first():
        errors['username'] = '该用户名已被使用'

    if nickname and len(nickname) > 50:
        errors['nickname'] = '昵称不能超过 50 个字符'
    elif nickname and User.query.filter_by(nickname=nickname).first():
        errors['nickname'] = '该昵称已被使用'

    if not email:
        errors['email'] = '请输入邮箱'
    elif not _EMAIL_RE.match(email):
        errors['email'] = '邮箱格式不正确'
    elif len(email) > 100:
        errors['email'] = '邮箱不能超过 100 个字符'
    elif User.query.filter_by(email=email).first():
        errors['email'] = '该邮箱已被使用'

    if len(password) < 6:
        errors['password'] = '密码至少 6 位'

    if errors:
        return jsonify({'success': False, 'message': '表单验证失败', 'errors': errors}), 400

    user = User(username=username, nickname=nickname or None, email=email, is_admin=False)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    login_user(user)
    return jsonify({
        'success': True,
        'message': f'注册成功，欢迎 {user.display_name}！',
        'user': user_to_dict(user),
    }), 201


@api_bp.route('/auth/login', methods=['POST'])
def login():
    """管理员登录（JSON body: username, password, remember）"""
    if current_user.is_authenticated:
        return jsonify({'success': True, 'user': user_to_dict(current_user)})

    data = request.get_json(silent=True) or {}
    username = (data.get('username') or '').strip()
    password = data.get('password') or ''

    if not username or not password:
        return jsonify({'success': False, 'message': '请输入用户名和密码'}), 400

    user = User.query.filter_by(username=username).first()
    if user is None or not user.check_password(password):
        return jsonify({'success': False, 'message': '用户名或密码错误'}), 401

    login_user(user, remember=bool(data.get('remember')))

    # 记录登录信息
    user.login_ip = get_client_ip()
    user.last_login = datetime.now()
    db.session.commit()

    return jsonify({'success': True, 'message': f'欢迎回来，{user.display_name}！', 'user': user_to_dict(user)})


@api_bp.route('/auth/logout', methods=['POST'])
@login_required
def logout():
    """管理员登出"""
    logout_user()
    return jsonify({'success': True, 'message': '您已成功登出'})


@api_bp.route('/auth/me', methods=['GET'])
def me():
    """获取当前登录状态（SPA 启动时恢复登录态）"""
    if current_user.is_authenticated:
        return jsonify({'authenticated': True, 'user': user_to_dict(current_user)})
    return jsonify({'authenticated': False, 'user': None})
