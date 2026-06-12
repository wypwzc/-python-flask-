"""
修改管理员密码脚本
用法: conda run -n cs python change_password.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ['DATABASE_URL'] = 'mysql+pymysql://root:123456@localhost:3306/blog_db'

from app import create_app, db
from app.models import User

app = create_app('development')
with app.app_context():
    user = User.query.filter_by(username='admin').first()
    if user:
        new_password = 'admin123'  # 改成你想要的密码
        user.set_password(new_password)
        db.session.commit()
        print(f'管理员密码已修改为: {new_password}')
    else:
        print('未找到管理员账号')
