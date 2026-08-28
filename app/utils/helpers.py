"""
通用辅助函数
包含 Markdown 渲染、时间格式化、文本处理等功能
"""
import re
import uuid
import os
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
from PIL import Image

import markdown as md_lib
import bleach


# Markdown 渲染配置
ALLOWED_TAGS = list(bleach.ALLOWED_TAGS) + [
    'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    'pre', 'code', 'blockquote',
    'table', 'thead', 'tbody', 'tr', 'th', 'td',
    'img', 'br', 'hr', 'figure', 'figcaption',
    'span', 'div', 'del', 'sup', 'sub',
    'ul', 'ol', 'li',
    'dl', 'dt', 'dd'
]

ALLOWED_ATTRS = {
    '*': ['class', 'id', 'style'],
    'img': ['src', 'alt', 'title', 'width', 'height'],
    'a': ['href', 'title', 'rel', 'target'],
    'code': ['class'],
    'pre': ['class'],
    'span': ['class'],
    'table': ['class'],
    'td': ['class', 'colspan', 'rowspan'],
    'th': ['class', 'colspan', 'rowspan'],
}


def render_markdown(content):
    """
    安全渲染 Markdown 内容为 HTML
    使用 bleach 清洗 HTML 防止 XSS 攻击

    :param content: Markdown 原始文本
    :return: 安全的 HTML 字符串
    """
    if not content:
        return ''

    # 配置 Markdown 扩展
    extensions = [
        'extra',                          # 包含 fenced_code, tables, footnotes 等
        'codehilite',                     # 代码高亮（配合 CSS）
        'toc',                            # 目录生成
        'sane_lists',                     # 合理的列表行为
        'smarty',                         # 智能引号
        'attr_list',                     # 属性列表
    ]

    extension_configs = {
        'codehilite': {
            'linenums': False,            # 不显示行号
            'css_class': 'highlight',     # CSS 类名
        },
        'toc': {
            'permalink': False,           # 不添加永久链接
        }
    }

    # 先渲染 Markdown
    html = md_lib.markdown(
        content,
        extensions=extensions,
        extension_configs=extension_configs
    )

    # 用 bleach 清洗 HTML，防止 XSS
    clean_html = bleach.clean(
        html,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRS,
        strip=True
    )

    return clean_html


def generate_slug(text):
    """
    从文本生成 URL 友好的 slug

    :param text: 原始文本
    :return: slug 字符串
    """
    # 转为小写
    slug = text.lower()
    # 替换空格为短横线
    slug = re.sub(r'\s+', '-', slug)
    # 移除非字母数字和短横线的字符
    slug = re.sub(r'[^a-z0-9\-]', '', slug)
    # 移除连续的短横线
    slug = re.sub(r'-+', '-', slug)
    # 移除首尾短横线
    slug = slug.strip('-')
    return slug


def save_upload_image(file, folder='uploads', max_size=(1200, 1200), quality=85):
    """
    保存上传的图片，自动压缩和生成缩略图

    :param file: FileStorage 对象
    :param folder: 存储子目录
    :param max_size: 最大尺寸（宽, 高）
    :param quality: JPEG 压缩质量
    :return: 保存后的相对路径
    """
    from flask import current_app

    # 生成安全的文件名
    original_filename = secure_filename(file.filename)
    ext = original_filename.rsplit('.', 1)[1].lower() if '.' in original_filename else 'jpg'
    # 使用 UUID 生成唯一文件名
    filename = f"{uuid.uuid4().hex}.{ext}"

    # 按日期分目录（如 uploads/2024/01/）
    today = datetime.now()
    date_path = today.strftime('%Y/%m')
    relative_path = f"{folder}/{date_path}"
    upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], date_path)

    # 确保目录存在
    os.makedirs(upload_dir, exist_ok=True)

    # 完整保存路径
    filepath = os.path.join(upload_dir, filename)

    # 使用 Pillow 处理图片
    img = Image.open(file)
    # 转换 RGBA 为 RGB（JPEG 不支持透明通道）
    if img.mode in ('RGBA', 'LA', 'P'):
        img = img.convert('RGB')

    # 调整尺寸
    img.thumbnail(max_size, Image.LANCZOS)

    # 保存（根据扩展名选择格式）
    if ext.lower() in ('jpg', 'jpeg'):
        img.save(filepath, 'JPEG', quality=quality, optimize=True)
    elif ext.lower() == 'png':
        img.save(filepath, 'PNG', optimize=True)
    elif ext.lower() == 'gif':
        img.save(filepath, 'GIF')
    elif ext.lower() == 'webp':
        img.save(filepath, 'WEBP', quality=quality)
    else:
        img.save(filepath, 'JPEG', quality=quality, optimize=True)

    # 返回相对路径（用于模板中的 url_for）
    return f"uploads/{date_path}/{filename}"


def save_avatar(file, max_size=(200, 200), quality=85):
    """
    保存头像图片（自动裁剪为正方形）

    :param file: FileStorage 对象
    :param max_size: 最大尺寸
    :param quality: 压缩质量
    :return: 保存后的相对路径
    """
    from flask import current_app

    original_filename = secure_filename(file.filename)
    ext = original_filename.rsplit('.', 1)[1].lower() if '.' in original_filename else 'jpg'
    filename = f"avatar_{uuid.uuid4().hex}.{ext}"

    upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'avatars')
    os.makedirs(upload_dir, exist_ok=True)

    filepath = os.path.join(upload_dir, filename)

    img = Image.open(file)
    # 裁剪为正方形（取短边）
    width, height = img.size
    min_side = min(width, height)
    left = (width - min_side) // 2
    top = (height - min_side) // 2
    img = img.crop((left, top, left + min_side, top + min_side))

    if img.mode in ('RGBA', 'LA', 'P'):
        img = img.convert('RGB')

    img.thumbnail(max_size, Image.LANCZOS)

    if ext.lower() in ('jpg', 'jpeg'):
        img.save(filepath, 'JPEG', quality=quality, optimize=True)
    else:
        img.save(filepath, 'PNG', optimize=True)

    return 'uploads/avatars/' + filename


def get_client_ip():
    """
    获取客户端真实 IP 地址
    支持代理情况下的 X-Forwarded-For 头

    :return: IP 地址字符串
    """
    from flask import request
    # 检查是否有代理转发
    if request.headers.get('X-Forwarded-For'):
        ip = request.headers.get('X-Forwarded-For').split(',')[0].strip()
    elif request.headers.get('X-Real-IP'):
        ip = request.headers.get('X-Real-IP')
    else:
        ip = request.remote_addr or '0.0.0.0'
    return ip
