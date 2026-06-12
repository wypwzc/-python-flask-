"""
博客系统启动入口
用法：python run.py
"""
import os
from app import create_app

# 从环境变量获取配置名称，默认为 development
config_name = os.getenv('FLASK_ENV', 'development')
app = create_app(config_name)

if __name__ == '__main__':
    # 获取主机和端口配置（从环境变量或使用默认值）
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_PORT', 5000))
    debug = config_name == 'development'

    print(f'✨ 博客系统启动中...')
    print(f'📝 配置环境: {config_name}')
    print(f'🔗 访问地址: http://{host}:{port}')
    print(f'🛑 按 Ctrl+C 停止服务器')

    app.run(host=host, port=port, debug=debug)
