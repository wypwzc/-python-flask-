# 个人博客系统

基于 Python + Flask + MySQL 构建的个人博客系统，功能完整、代码清晰、响应式设计。

## 技术栈

| 层级 | 技术选型 | 说明 |
|------|---------|------|
| 后端框架 | Flask 3.x | 使用 Flask-SQLAlchemy ORM |
| 数据库 | MySQL 8.0 | PyMySQL 驱动 |
| 模板引擎 | Jinja2 | Flask 原生支持 |
| 前端样式 | Bootstrap 5 | 响应式布局，支持移动端 |
| Markdown | python-markdown + bleach | 安全渲染，防止 XSS |
| 密码加密 | werkzeug.security | pbkdf2:sha256 加密 |
| 表单验证 | Flask-WTF | CSRF 保护 + 表单校验 |
| 图片处理 | Pillow | 头像裁剪、图片压缩 |

## 功能特性

### ✅ 已实现功能

- **首页展示**：文章列表、置顶、分页、侧边栏（分类/标签云/热门文章/最新留言）
- **文章详情**：Markdown 渲染、代码高亮、TOC 目录、阅读量统计、上一篇/下一篇
- **分类与标签**：分类/标签筛选页面，支持分页
- **后台管理**：仪表盘（统计图表）、文章/分类/标签/留言/友链管理
- **用户系统**：登录/登出、密码加密、会话安全、@login_required 保护
- **留言评论**：全站留言板、文章评论、嵌套回复、IP 记录
- **主题切换**：日间/夜间模式，跟随系统偏好，localStorage 保存
- **全文搜索**：支持标题、内容、摘要搜索
- **文章归档**：按年份/月份分组，时间轴样式
- **友情链接**：排序、启用/禁用管理
- **访问统计**：PV/UV 统计，按天汇总
- **文章点赞**：IP 防重复点赞
- **图片上传**：封面图、头像，自动压缩
- **响应式设计**：完美适配移动端
- **数据校验**：表单验证、错误处理（404/500 页面）

## 快速开始

### 环境要求

- Python 3.9+
- MySQL 8.0
- pip（Python 包管理器）

### 1. 克隆项目

```bash
cd blog
```

### 2. 创建虚拟环境（推荐）

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 配置数据库

确保 MySQL 服务已启动，然后创建数据库：

```bash
# 登录 MySQL
mysql -u root -p

# 创建数据库
CREATE DATABASE blog_db DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 5. 配置环境变量

编辑 `.env` 文件，修改数据库连接信息：

```env
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
DATABASE_URL=mysql+pymysql://root:your_password@localhost:3306/blog_db
```

### 6. 初始化数据库

```bash
python init_db.py
```

默认会创建：
- 管理员账号：`admin` / `admin123`
- 4 个默认分类
- 8 个默认标签
- 1 篇示例文章

### 7. 启动服务

```bash
python run.py
```

访问地址：
- 前台首页：http://localhost:5000
- 后台管理：http://localhost:5000/admin
- 登录页面：http://localhost:5000/auth/login

## 项目结构

```
blog/
├── app/
│   ├── __init__.py          # 应用工厂
│   ├── models/              # 数据模型
│   │   ├── user.py          # 用户模型
│   │   ├── post.py          # 文章模型
│   │   ├── category.py      # 分类模型
│   │   ├── tag.py           # 标签模型
│   │   ├── comment.py       # 评论模型
│   │   ├── link.py          # 友链模型
│   │   ├── site_stats.py    # 统计模型
│   │   └── post_like.py     # 点赞记录
│   ├── views/               # 路由视图
│   │   ├── front.py         # 前台路由
│   │   ├── admin.py         # 后台路由
│   │   └── auth.py          # 认证路由
│   ├── forms/               # WTForms 表单
│   ├── utils/               # 工具函数
│   ├── static/              # 静态资源
│   └── templates/           # 模板文件
├── config.py                # 配置文件
├── run.py                   # 启动入口
├── init_db.py               # 数据库初始化
├── requirements.txt         # 依赖列表
└── .env                     # 环境变量
```

## 部署说明

### 生产环境配置

1. 修改 `.env` 中的配置：
   ```env
   FLASK_ENV=production
   SECRET_KEY=生成一个安全的随机密钥
   ```

2. 使用 Gunicorn 或 uWSGI 部署：
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:8000 "app:create_app('production')"
   ```

3. 配置 Nginx 反向代理（推荐）

### Docker 部署（可选）

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "app:create_app('production')"]
```

## 安全建议

1. **立即修改默认密码**：登录后请立即修改管理员密码
2. **设置强密码**：建议使用 8 位以上，包含大小写字母和数字
3. **生成安全密钥**：用 `python -c "import secrets; print(secrets.token_hex(32))"` 生成 SECRET_KEY
4. **启用 HTTPS**：生产环境务必配置 SSL 证书
5. **定期备份**：建议定期备份数据库和上传文件

## License

MIT License
