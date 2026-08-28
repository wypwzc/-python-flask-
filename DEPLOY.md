# 云服务器 Docker 部署指南

本项目已提供 Docker 化部署所需全部文件：

| 文件 | 作用 |
|------|------|
| `Dockerfile` | 多阶段构建：Node 构建前端 → Python 运行 Flask |
| `docker-compose.yml` | 一键启动 MySQL 8 + Flask 应用 + Nginx 三个容器 |
| `nginx/nginx.conf` | Nginx 配置：80→443 跳转、443 前台、5888 后台 |
| `.dockerignore` | 排除 `.env`、node_modules 等 |

**架构**：浏览器 → Nginx（80/443/5888）→ Flask 容器（5000 前台 / 5888 后台）→ MySQL 容器

- 前台：`https://你的域名`
- 后台：`https://你的域名:5888`（登录页 `/master`）
- 端口分流逻辑在前端（检测 `location.port === '5888'`），**项目代码零改动**。

---

## 一、服务器准备

```bash
# 1. 安装 Docker 与 Compose 插件（以 Ubuntu/Debian 为例）
curl -fsSL https://get.docker.com | bash
sudo systemctl enable --now docker
sudo apt-get install -y docker-compose-plugin

# 2. 验证
docker --version
docker compose version
```

**云服务商安全组/防火墙放行端口**：`80`、`443`、`5888`（TCP）。域名解析（A 记录）指向服务器公网 IP。

## 二、上传项目代码

```bash
# 服务器上执行（任选其一）
# 方式 A：git clone（推荐）
git clone https://github.com/wypwzc/-python-flask-.git blog
cd blog

# 方式 B：本地打包上传
#   本地执行: tar czf blog.tgz --exclude='.git' --exclude='node_modules' blog
#   scp blog.tgz 用户名@服务器IP:~/
#   服务器执行: tar xzf blog.tgz && cd blog
```

> `.env`（本地数据库密码等敏感配置）在 `.gitignore` / `.dockerignore` 中，不会随仓库上传，服务器上需重新创建，见下一步。

## 三、服务器配置

### 1. 创建 `.env`（在项目根目录）

```bash
cp .env.example .env   # 若没有示例则手动创建，内容如下
vi .env
```

```ini
# 数据库 root 密码（务必修改成强密码！首次部署决定，改后需删除 mysql_data 卷重建）
MYSQL_ROOT_PASSWORD=你的强密码

# 会话密钥（用命令生成随机值: openssl rand -hex 32）
SECRET_KEY=用openssl生成的32字节hex

# 邮件通知（可选，留空则不发邮件，不影响使用）
MAIL_SERVER=smtp.qq.com
MAIL_PORT=465
MAIL_USE_TLS=False
MAIL_USERNAME=你的邮箱
MAIL_PASSWORD=邮箱授权码
ADMIN_EMAIL=你的邮箱
```

### 2. 确认证书路径

证书文件已放在服务器 `/root/ssl/`：
- `www.wzcwyp.xyz.pem`（证书）
- `www.wzcwyp.xyz.key`（私钥）

`nginx/nginx.conf` 和 `docker-compose.yml` **已按此配置好（域名 www.wzcwyp.xyz、证书目录 /root/ssl），无需修改**。

注意：证书只覆盖 `www.wzcwyp.xyz` 子域，请使用 `https://www.wzcwyp.xyz` 访问（裸域 HTTP 会自动 301 跳转到 www；裸域 HTTPS 因证书不含裸域会提示不安全，建议始终用 www）。

> 如果以后更换证书位置，改两处即可：
> 1. `docker-compose.yml` 中 nginx 的 `volumes`：挂载证书所在目录
> 2. `nginx/nginx.conf` 中 `ssl_certificate` / `ssl_certificate_key` 两个路径

## 四、构建并启动

```bash
# 首次构建（拉取基础镜像 + 安装依赖 + 构建前端，约 5-10 分钟）
sudo docker compose up -d --build

# 查看状态与日志
sudo docker compose ps
sudo docker compose logs -f app      # 应用日志（Ctrl+C 退出查看）
```

启动过程：MySQL 健康检查通过 → 应用容器跑 `init_db.py`（自动建表 + 创建管理员 `admin`/`admin123` + 示例文章，幂等）→ Nginx 就绪。

## 五、验证

| 验证项 | 地址 |
|--------|------|
| 前台 | `https://www.wzcwyp.xyz`（能看到示例文章"欢迎来到个人博客！"） |
| 后台 | `https://www.wzcwyp.xyz:5888` → 登录 `admin` / `admin123` |
| 写文章 | 后台 → 写文章 → 填标题和 Markdown 正文 → 发布 |

**首次登录后请立即修改 admin 密码**（后台 → 个人设置）。

## 六、日常运维

```bash
# 查看所有容器状态
sudo docker compose ps

# 查看日志（跟踪模式）
sudo docker compose logs -f

# 重启
sudo docker compose restart

# 更新部署（拉最新代码后）
git pull
sudo docker compose up -d --build

# 停止
sudo docker compose down

# 完全清除（含数据库数据，慎用！）
sudo docker compose down -v

# 备份数据库
sudo docker compose exec mysql sh -c 'exec mysqldump -uroot -p"$MYSQL_ROOT_PASSWORD" blog_db' > backup_$(date +%F).sql

# 恢复数据库
sudo docker compose exec -T mysql sh -c 'exec mysql -uroot -p"$MYSQL_ROOT_PASSWORD" blog_db' < backup_xxx.sql
```

## 常见问题

- **后台登录失败/一直跳登录**：确认你是通过 `https://你的域名:5888` 访问（不是 5000/HTTP）；生产模式 session cookie 仅 HTTPS 下生效
- **上传图片失败**：检查 Nginx `client_max_body_size`（已设为 10m）与后端 5MB 限制
- **改代码后不生效**：`sudo docker compose up -d --build` 重新构建镜像
- **端口被占**：`sudo ss -tlnp | grep -E ':(80|443|5888)'` 查看占用
