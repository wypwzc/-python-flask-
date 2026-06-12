"""
认证路由 - 登录/登出
仅管理员使用，登录后跳转后台仪表盘
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models.user import User
from app.forms.login_form import LoginForm
from app.utils.helpers import get_client_ip

from datetime import datetime

auth_bp = Blueprint('auth', __name__, template_folder='../templates/auth')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    管理员登录
    GET: 展示登录页面
    POST: 验证用户名密码并登录
    """
    # 如果已经登录，重定向到后台
    if current_user.is_authenticated:
        return redirect(url_for('admin.dashboard'))

    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data.strip()
        password = form.password.data
        remember = form.remember_me.data

        # 查询用户
        user = User.query.filter_by(username=username).first()

        # 验证用户名和密码
        if user is not None and user.check_password(password):
            # 登录成功
            login_user(user, remember=remember)

            # 记录登录信息
            user.login_ip = get_client_ip()
            user.last_login = datetime.now()
            db.session.commit()

            flash(f'欢迎回来，{user.display_name}！', 'success')

            # 跳转到之前请求的页面或后台首页
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(url_for('admin.dashboard'))
        else:
            flash('用户名或密码错误', 'danger')

    return render_template('auth/login.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    """
    管理员登出
    清除登录状态并跳转到首页
    """
    logout_user()
    flash('您已成功登出', 'info')
    return redirect(url_for('front.index'))
