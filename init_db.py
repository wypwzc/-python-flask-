"""
数据库初始化脚本
自动创建数据库表并插入默认管理员账号

用法：
    python init_db.py          # 初始化数据库
    python init_db.py --reset  # 重置数据库（删除所有表后重建）
"""
import sys
import os
from datetime import datetime  # 用于示例文章

# 将项目根目录加入 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models.user import User
from app.models.category import Category
from app.models.tag import Tag
from app.models.post import Post
from app.models.comment import Comment
from app.models.link import Link
from app.models.site_stats import SiteStats
from app.models.post_like import PostLike
from app.models.post_tags import post_tags


def init_database(reset=False):
    """
    初始化数据库

    :param reset: 是否重置数据库（删除所有表后重建）
    """
    app = create_app('development')

    with app.app_context():
        if reset:
            print('⚠️  正在重置数据库...')
            db.drop_all()
            print('✅ 已删除所有数据表')

        # 创建所有表
        db.create_all()
        print('✅ 数据库表创建完成')

        # 检查是否已存在管理员账号
        admin = User.query.filter_by(is_admin=True).first()
        if not admin:
            # 创建默认管理员账号
            admin = User(
                username='admin',
                email='admin@example.com',
                nickname='管理员',
                bio='博客管理员',
                is_admin=True
            )
            admin.set_password('admin123')  # 默认密码，部署后请立即修改
            db.session.add(admin)
            db.session.commit()
            print('✅ 默认管理员账号已创建')
            print('   └─ 用户名: admin')
            print('   └─ 密码: admin123')
            print('   └─ 请登录后立即修改密码！')
        else:
            print('ℹ️  管理员账号已存在，跳过创建')

        # 创建默认分类
        default_categories = [
            {'name': '技术笔记', 'slug': 'tech-notes', 'description': '技术相关文章'},
            {'name': '生活随笔', 'slug': 'life', 'description': '生活感悟与随笔'},
            {'name': '资源分享', 'slug': 'resources', 'description': '优质资源推荐'},
            {'name': '项目实战', 'slug': 'projects', 'description': '项目开发经验'},
        ]

        for cat_data in default_categories:
            existing = Category.query.filter_by(slug=cat_data['slug']).first()
            if not existing:
                category = Category(**cat_data)
                db.session.add(category)

        # 创建默认标签
        default_tags = [
            {'name': 'Python', 'slug': 'python'},
            {'name': 'Flask', 'slug': 'flask'},
            {'name': 'JavaScript', 'slug': 'javascript'},
            {'name': '前端', 'slug': 'frontend'},
            {'name': '数据库', 'slug': 'database'},
            {'name': '运维', 'slug': 'devops'},
            {'name': '教程', 'slug': 'tutorial'},
            {'name': '开源', 'slug': 'open-source'},
        ]

        for tag_data in default_tags:
            existing = Tag.query.filter_by(slug=tag_data['slug']).first()
            if not existing:
                tag = Tag(**tag_data)
                db.session.add(tag)

        # 创建示例文章（可选）
        create_sample = os.getenv('CREATE_SAMPLE_DATA', 'true').lower() == 'true'
        if create_sample and not Post.query.first():
            category = Category.query.filter_by(slug='tech-notes').first()
            author = User.query.filter_by(is_admin=True).first()

            if category and author:
                sample_post = Post(
                    title='欢迎来到个人博客！',
                    slug='welcome',
                    summary='这是博客的第一篇文章，介绍了博客的基本功能和使用方法。',
                    content='''# 欢迎来到个人博客！

感谢你选择使用这个博客系统！这里是你分享技术、记录生活的理想平台。

## 主要功能

- 📝 **Markdown 编辑**：使用熟悉的 Markdown 语法撰写文章
- 🏷️ **分类与标签**：方便的文章分类和标签管理
- 💬 **评论系统**：访客留言与互动
- 🔍 **全文搜索**：快速查找所需内容
- 🌙 **夜间模式**：舒适的阅读体验

## 快速开始

1. 登录后台管理 `/admin`
2. 创建文章分类和标签
3. 撰写你的第一篇文章
4. 在「关于」页面编辑个人介绍

## Markdown 示例

### 代码高亮

```python
def hello():
    print("Hello, World!")
```

### 表格

| 功能 | 说明 |
|------|------|
| Markdown | 支持代码高亮和扩展语法 |
| 夜间模式 | 自动跟随系统或手动切换 |
| 响应式 | 完美适配移动端访问 |

### 引用

> 分享知识，传递价值。
> 让每一次创作都有意义。

---

祝你使用愉快！如果遇到任何问题，欢迎在留言板留言反馈。
''',
                    category_id=category.id,
                    author_id=author.id,
                    is_published=True,
                    is_top=True,
                    published_at=datetime.now()
                )
                db.session.add(sample_post)

                # 添加标签
                welcome_tag = Tag.query.filter_by(slug='tutorial').first()
                if welcome_tag:
                    sample_post.tags.append(welcome_tag)

                print('✅ 示例文章已创建')

        db.session.commit()
        print()
        print('🎉 数据库初始化完成！')
        print()
        print('📝 启动方式：')
        print('   python run.py')
        print()
        print('🔗 访问地址：')
        print('   前台: http://localhost:5000')
        print('   后台: http://localhost:5000/admin')
        print('   登录: http://localhost:5000/auth/login')


if __name__ == '__main__':
    # 从命令行判断是否需要重置
    reset = '--reset' in sys.argv

    print('=' * 50)
    print('📦 博客系统 - 数据库初始化')
    print('=' * 50)
    print()

    init_database(reset=reset)
