# ========== 阶段 1：构建前端（Vue 3 SPA） ==========
FROM node:20-alpine AS frontend
WORKDIR /build
# 先装依赖再复制源码（利用层缓存加速构建）
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# ========== 阶段 2：Python 运行环境 ==========
FROM python:3.11-slim
WORKDIR /app

# 依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 项目代码（.dockerignore 已排除 .env / node_modules / .git 等）
COPY . .
# 前端构建产物（Flask 托管）
COPY --from=frontend /build/dist ./frontend/dist

# 双端口：5000 前台 / 5888 后台
EXPOSE 5000 5888

# 首次启动初始化数据库（幂等：已有表/管理员/示例文章时自动跳过），然后启动双端口服务
CMD ["sh", "-c", "python init_db.py && python run.py"]
