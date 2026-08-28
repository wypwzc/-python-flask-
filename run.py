"""
博客系统启动入口（双端口）
- 前台 5000：博客浏览 + 普通用户登录/注册/评论留言
- 后台 5888：管理员登录(/master) + 后台管理(/admin)

两个端口共享同一个 Flask 应用（同一 MySQL、同一 session/CSRF cookie），
浏览器 cookie 不区分端口，管理员在前台/后台任一端口登录后两处都生效。

用法：python run.py
"""
import os
import threading

from werkzeug.serving import make_server

from app import create_app

# 从环境变量获取配置名称，默认为 development
config_name = os.getenv('FLASK_ENV', 'development')
app = create_app(config_name)

ADMIN_PORT = int(os.getenv('FLASK_ADMIN_PORT', '5888'))


def _serve(host, port, label):
    """启动一个端口的 WSGI 服务（独立线程）"""
    server = make_server(host, port, app)
    print(f'🔗 {label}: http://{host}:{port}')
    server.serve_forever()


if __name__ == '__main__':
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_PORT', '5000'))

    print(f'✨ 博客系统启动中...')
    print(f'📝 配置环境: {config_name}')
    print(f'🛑 按 Ctrl+C 停止服务器')

    # 后台端口独立线程（前台在主线运行）
    threading.Thread(target=_serve, args=(host, ADMIN_PORT, '后台'), daemon=True).start()
    _serve(host, port, '前台')
