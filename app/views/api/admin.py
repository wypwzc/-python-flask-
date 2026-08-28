"""
后台管理 API - 仅管理员可访问（admin_required）
仪表盘、文章 CRUD、分类/标签/友链 CRUD、评论审核、个人资料
"""
import re
from datetime import datetime

from flask import jsonify, request, current_app
from flask_login import current_user
from email_validator import validate_email, EmailNotValidError

from app import db
from app.models.user import User
from app.models.post import Post
from app.models.category import Category
from app.models.tag import Tag
from app.models.comment import Comment
from app.models.link import Link
from app.models.site_stats import SiteStats
from app.utils.decorators import admin_required
from app.utils.helpers import render_markdown, save_upload_image, save_avatar, \
    generate_slug, get_client_ip
from app.views.api import api_bp
from app.views.api.serializers import (
    post_to_dict, comment_to_dict, category_to_dict, tag_to_dict,
    link_to_dict, user_to_dict, pagination_to_dict,
)

SLUG_RE = re.compile(r'^[a-z0-9\-]+$')


# ─── 工具函数 ────────────────────────────────────────────

def _get_page_params(default_per_page=15, max_per_page=50):
    page = request.args.get('page', 1, type=int) or 1
    per_page = request.args.get('per_page', default_per_page, type=int) or default_per_page
    page = max(page, 1)
    per_page = min(max(per_page, 1), max_per_page)
    return page, per_page


def _is_valid_email(email):
    try:
        validate_email(email, check_deliverability=False)
        return True
    except EmailNotValidError:
        return False


def _parse_bool(value, default=False):
    """解析 JSON 布尔值（兼容 0/1）"""
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, str)) and str(value) in ('1', '0', 'true', 'false', 'True', 'False'):
        return str(value).lower() in ('1', 'true')
    return default


def _ensure_unique_slug(model, slug, exclude_id=None):
    """slug 唯一性校验，返回冲突对象或 None"""
    query = model.query.filter_by(slug=slug)
    if exclude_id:
        query = query.filter(model.id != exclude_id)
    return query.first()


def _process_post_tags(post, tag_names):
    """
    处理文章的标签关联（创建不存在的标签，更新计数）
    :param post: Post 对象
    :param tag_names: 标签名称列表
    """
    tags = []
    for name in tag_names:
        tag = Tag.query.filter_by(name=name).first()
        if not tag:
            slug = generate_slug(name)
            base_slug = slug
            counter = 1
            while Tag.query.filter_by(slug=slug).first():
                slug = f'{base_slug}-{counter}'
                counter += 1
            tag = Tag(name=name, slug=slug)
            db.session.add(tag)
            db.session.flush()
        tags.append(tag)

    # 更新计数：新旧标签的并集
    affected = set(tags) | set(post.tags)
    post.tags = tags
    db.session.flush()
    for tag in affected:
        tag.update_post_count()


def _apply_post_fields(post, data):
    """将校验后的数据应用到 Post 对象"""
    post.title = data['title']
    post.slug = data['slug']
    post.summary = data.get('summary') or None
    post.content = data['content']
    post.category_id = data.get('category_id')
    post.cover_image = data.get('cover_image') or None
    post.is_published = data.get('is_published', True)
    post.is_top = data.get('is_top', False)
    post.allow_comment = data.get('allow_comment', True)
    if post.is_published and not post.published_at:
        post.published_at = datetime.now()
    post.content_html = render_markdown(post.content)


def _validate_post_data(data, exclude_id=None):
    """
    校验文章数据
    :return: (errors, cleaned_data)；errors 为 None 表示通过
    """
    errors = {}

    title = (data.get('title') or '').strip()
    content = (data.get('content') or '').strip()
    summary = (data.get('summary') or '').strip()

    if not title:
        errors['title'] = '请输入文章标题'
    elif len(title) > 200:
        errors['title'] = '标题长度为 1-200 个字符'

    if not content:
        errors['content'] = '请输入文章内容'

    if len(summary) > 500:
        errors['summary'] = '摘要不超过 500 个字符'

    # slug：为空时自动从标题生成（中文标题生成结果为空则用随机后缀兜底）
    from uuid import uuid4
    slug = (data.get('slug') or '').strip() or generate_slug(title) or f'post-{uuid4().hex[:8]}'
    if len(slug) > 200:
        errors['slug'] = 'URL 别名为 1-200 个字符'
    elif not SLUG_RE.match(slug):
        errors['slug'] = 'URL 别名只能包含小写字母、数字和短横线'
    elif _ensure_unique_slug(Post, slug, exclude_id):
        errors['slug'] = '该 URL 别名已被使用'

    # 分类
    category_id = data.get('category_id')
    if category_id in (None, '', 0, '0'):
        cleaned_category_id = None
    elif str(category_id).isdigit():
        cleaned_category_id = int(category_id)
        if not Category.query.get(cleaned_category_id):
            errors['category_id'] = '所选分类不存在'
    else:
        cleaned_category_id = None
        errors['category_id'] = '分类参数无效'

    # 标签
    tags_raw = data.get('tags', [])
    if isinstance(tags_raw, str):
        tags = [t.strip() for t in tags_raw.split(',') if t.strip()]
    elif isinstance(tags_raw, list):
        tags = [str(t).strip() for t in tags_raw if str(t).strip()]
    else:
        tags = []
    for name in tags:
        if len(name) > 50:
            errors['tags'] = '标签名不能超过 50 个字符'
            break

    if errors:
        return errors, None

    return None, {
        'title': title,
        'slug': slug,
        'summary': summary,
        'content': content,
        'category_id': cleaned_category_id,
        'cover_image': (data.get('cover_image') or '').strip() or None,
        'is_published': _parse_bool(data.get('is_published'), True),
        'is_top': _parse_bool(data.get('is_top'), False),
        'allow_comment': _parse_bool(data.get('allow_comment'), True),
        'tags': tags,
    }


# ─── 仪表盘 ──────────────────────────────────────────────

@api_bp.route('/admin/dashboard/stats', methods=['GET'])
@admin_required
def dashboard_stats():
    """仪表盘统计（卡片 + 7 天趋势 + 最新数据）"""
    recent_stats_raw = SiteStats.get_recent_days(7)
    recent_stats = [
        {'date': s.date.strftime('%Y-%m-%d'), 'pv': s.pv or 0, 'uv': s.uv or 0}
        for s in recent_stats_raw
    ]
    return jsonify({
        'counts': {
            'posts': Post.query.count(),
            'categories': Category.query.count(),
            'tags': Tag.query.count(),
            'comments': Comment.query.count(),
            'pending_comments': Comment.query.filter_by(is_approved=False).count(),
        },
        'total_stats': SiteStats.get_total_stats(),
        'recent_stats': recent_stats,
        'recent_posts': [post_to_dict(p) for p in Post.query.order_by(Post.created_at.desc()).limit(5).all()],
        'recent_comments': [
            {**comment_to_dict(c), 'post_title': c.post.title if c.post else '全站留言板'}
            for c in Comment.query.order_by(Comment.created_at.desc()).limit(5).all()
        ],
    })


# ─── 文章管理 ────────────────────────────────────────────

@api_bp.route('/admin/posts', methods=['GET'])
@admin_required
def admin_post_list():
    """文章列表（含草稿，支持搜索/分类/发布状态筛选）"""
    page, per_page = _get_page_params()
    search = (request.args.get('q') or '').strip()
    category_id = request.args.get('category_id', type=int)
    status = request.args.get('status', '').strip()

    query = Post.query

    if search:
        query = query.filter(Post.title.contains(search))
    if category_id:
        query = query.filter_by(category_id=category_id)
    if status == 'published':
        query = query.filter_by(is_published=True)
    elif status == 'draft':
        query = query.filter_by(is_published=False)

    query = query.order_by(Post.is_top.desc(), Post.created_at.desc())
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    items = [post_to_dict(p) for p in pagination.items]
    return jsonify(pagination_to_dict(pagination, items))


@api_bp.route('/admin/posts/<int:post_id>', methods=['GET'])
@admin_required
def admin_post_detail(post_id):
    """文章详情（编辑用，含 Markdown 原文）"""
    post = Post.query.get_or_404(post_id)
    return jsonify({'post': post_to_dict(post, include_content=True)})


@api_bp.route('/admin/posts', methods=['POST'])
@admin_required
def admin_post_create():
    """新增文章"""
    data = request.get_json(silent=True) or {}
    errors, cleaned = _validate_post_data(data)
    if errors:
        return jsonify({'success': False, 'message': '表单验证失败', 'errors': errors}), 400

    post = Post(author_id=current_user.id)
    _apply_post_fields(post, cleaned)
    db.session.add(post)
    db.session.commit()
    _process_post_tags(post, cleaned['tags'])
    db.session.commit()

    return jsonify({'success': True, 'message': '文章创建成功！', 'post': post_to_dict(post)}), 201


@api_bp.route('/admin/posts/<int:post_id>', methods=['PUT'])
@admin_required
def admin_post_update(post_id):
    """更新文章"""
    post = Post.query.get_or_404(post_id)
    data = request.get_json(silent=True) or {}
    errors, cleaned = _validate_post_data(data, exclude_id=post.id)
    if errors:
        return jsonify({'success': False, 'message': '表单验证失败', 'errors': errors}), 400

    _apply_post_fields(post, cleaned)
    db.session.commit()
    _process_post_tags(post, cleaned['tags'])
    db.session.commit()

    return jsonify({'success': True, 'message': '文章更新成功！', 'post': post_to_dict(post)})


@api_bp.route('/admin/posts/<int:post_id>', methods=['DELETE'])
@admin_required
def admin_post_delete(post_id):
    """删除文章"""
    post = Post.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    return jsonify({'success': True, 'message': '文章已删除'})


@api_bp.route('/admin/posts/batch-delete', methods=['POST'])
@admin_required
def admin_post_batch_delete():
    """批量删除文章"""
    data = request.get_json(silent=True) or {}
    ids = data.get('ids', [])
    if not isinstance(ids, list) or not ids:
        return jsonify({'success': False, 'message': '请选择要删除的文章'}), 400

    Post.query.filter(Post.id.in_(ids)).delete(synchronize_session=False)
    db.session.commit()
    return jsonify({'success': True, 'message': f'已删除 {len(ids)} 篇文章'})


@api_bp.route('/admin/posts/<int:post_id>/toggle-top', methods=['POST'])
@admin_required
def admin_post_toggle_top(post_id):
    """切换置顶状态"""
    post = Post.query.get_or_404(post_id)
    post.is_top = not post.is_top
    db.session.commit()
    return jsonify({'success': True, 'is_top': post.is_top})


@api_bp.route('/admin/posts/<int:post_id>/toggle-publish', methods=['POST'])
@admin_required
def admin_post_toggle_publish(post_id):
    """切换发布状态"""
    post = Post.query.get_or_404(post_id)
    post.is_published = not post.is_published
    if post.is_published and not post.published_at:
        post.published_at = datetime.now()
    db.session.commit()
    return jsonify({'success': True, 'is_published': post.is_published})


@api_bp.route('/admin/posts/render-preview', methods=['POST'])
@admin_required
def admin_post_render_preview():
    """Markdown 预览（服务端渲染，与最终保存渲染一致）"""
    data = request.get_json(silent=True) or {}
    content = data.get('content') or ''
    return jsonify({'html': render_markdown(content)})


# ─── 图片上传 ────────────────────────────────────────────

@api_bp.route('/admin/upload/cover', methods=['POST'])
@admin_required
def admin_upload_cover():
    """上传封面图"""
    file = request.files.get('file')
    if not file:
        return jsonify({'success': False, 'message': '未接收到文件'}), 400
    try:
        path = save_upload_image(file, folder='covers')
        return jsonify({'success': True, 'path': path})
    except Exception as e:
        current_app.logger.error(f'封面上传失败: {e}')
        return jsonify({'success': False, 'message': f'图片上传失败: {str(e)}'}), 400


@api_bp.route('/admin/upload/avatar', methods=['POST'])
@admin_required
def admin_upload_avatar():
    """上传头像"""
    file = request.files.get('file')
    if not file:
        return jsonify({'success': False, 'message': '未接收到文件'}), 400
    try:
        path = save_avatar(file)
        return jsonify({'success': True, 'path': path})
    except Exception as e:
        current_app.logger.error(f'头像上传失败: {e}')
        return jsonify({'success': False, 'message': f'头像上传失败: {str(e)}'}), 400


# ─── 分类管理 ────────────────────────────────────────────

def _validate_category_data(data, exclude_id=None):
    errors = {}
    name = (data.get('name') or '').strip()
    slug = (data.get('slug') or '').strip()
    description = (data.get('description') or '').strip()

    if not name:
        errors['name'] = '请输入分类名称'
    elif len(name) > 50:
        errors['name'] = '名称为 1-50 个字符'
    elif Category.query.filter(Category.name == name, Category.id != (exclude_id or 0)).first():
        errors['name'] = '该分类名称已存在'

    if not slug:
        errors['slug'] = '请输入 URL 别名'
    elif len(slug) > 50:
        errors['slug'] = '别名为 1-50 个字符'
    elif not SLUG_RE.match(slug):
        errors['slug'] = 'URL 别名只能包含小写字母、数字和短横线'
    elif _ensure_unique_slug(Category, slug, exclude_id):
        errors['slug'] = '该 URL 别名已被使用'

    if len(description) > 200:
        errors['description'] = '描述不超过 200 个字符'

    if errors:
        return errors, None
    return None, {'name': name, 'slug': slug, 'description': description or None}


@api_bp.route('/admin/categories', methods=['GET'])
@admin_required
def admin_category_list():
    categories = Category.query.order_by(Category.post_count.desc(), Category.name).all()
    return jsonify({'items': [category_to_dict(c) for c in categories]})


@api_bp.route('/admin/categories', methods=['POST'])
@admin_required
def admin_category_create():
    data = request.get_json(silent=True) or {}
    errors, cleaned = _validate_category_data(data)
    if errors:
        return jsonify({'success': False, 'message': '表单验证失败', 'errors': errors}), 400

    category = Category(**cleaned)
    db.session.add(category)
    db.session.commit()
    return jsonify({'success': True, 'message': '分类创建成功！', 'category': category_to_dict(category)}), 201


@api_bp.route('/admin/categories/<int:category_id>', methods=['PUT'])
@admin_required
def admin_category_update(category_id):
    category = Category.query.get_or_404(category_id)
    data = request.get_json(silent=True) or {}
    errors, cleaned = _validate_category_data(data, exclude_id=category.id)
    if errors:
        return jsonify({'success': False, 'message': '表单验证失败', 'errors': errors}), 400

    category.name = cleaned['name']
    category.slug = cleaned['slug']
    category.description = cleaned['description']
    db.session.commit()
    return jsonify({'success': True, 'message': '分类更新成功！', 'category': category_to_dict(category)})


@api_bp.route('/admin/categories/<int:category_id>', methods=['DELETE'])
@admin_required
def admin_category_delete(category_id):
    category = Category.query.get_or_404(category_id)
    if category.post_count > 0:
        return jsonify({
            'success': False,
            'message': f'分类 "{category.name}" 下有 {category.post_count} 篇文章，无法删除'
        }), 400
    db.session.delete(category)
    db.session.commit()
    return jsonify({'success': True, 'message': '分类已删除'})


# ─── 标签管理 ────────────────────────────────────────────

def _validate_tag_data(data, exclude_id=None):
    errors = {}
    name = (data.get('name') or '').strip()
    slug = (data.get('slug') or '').strip()

    if not name:
        errors['name'] = '请输入标签名称'
    elif len(name) > 50:
        errors['name'] = '名称为 1-50 个字符'
    elif Tag.query.filter(Tag.name == name, Tag.id != (exclude_id or 0)).first():
        errors['name'] = '该标签名称已存在'

    if not slug:
        errors['slug'] = '请输入 URL 别名'
    elif len(slug) > 50:
        errors['slug'] = '别名为 1-50 个字符'
    elif not SLUG_RE.match(slug):
        errors['slug'] = 'URL 别名只能包含小写字母、数字和短横线'
    elif _ensure_unique_slug(Tag, slug, exclude_id):
        errors['slug'] = '该 URL 别名已被使用'

    if errors:
        return errors, None
    return None, {'name': name, 'slug': slug}


@api_bp.route('/admin/tags', methods=['GET'])
@admin_required
def admin_tag_list():
    tags = Tag.query.order_by(Tag.post_count.desc(), Tag.name).all()
    return jsonify({'items': [tag_to_dict(t) for t in tags]})


@api_bp.route('/admin/tags', methods=['POST'])
@admin_required
def admin_tag_create():
    data = request.get_json(silent=True) or {}
    errors, cleaned = _validate_tag_data(data)
    if errors:
        return jsonify({'success': False, 'message': '表单验证失败', 'errors': errors}), 400

    tag = Tag(**cleaned)
    db.session.add(tag)
    db.session.commit()
    return jsonify({'success': True, 'message': '标签创建成功！', 'tag': tag_to_dict(tag)}), 201


@api_bp.route('/admin/tags/<int:tag_id>', methods=['PUT'])
@admin_required
def admin_tag_update(tag_id):
    tag = Tag.query.get_or_404(tag_id)
    data = request.get_json(silent=True) or {}
    errors, cleaned = _validate_tag_data(data, exclude_id=tag.id)
    if errors:
        return jsonify({'success': False, 'message': '表单验证失败', 'errors': errors}), 400

    tag.name = cleaned['name']
    tag.slug = cleaned['slug']
    db.session.commit()
    return jsonify({'success': True, 'message': '标签更新成功！', 'tag': tag_to_dict(tag)})


@api_bp.route('/admin/tags/<int:tag_id>', methods=['DELETE'])
@admin_required
def admin_tag_delete(tag_id):
    tag = Tag.query.get_or_404(tag_id)
    db.session.delete(tag)
    db.session.commit()
    return jsonify({'success': True, 'message': '标签已删除'})


# ─── 友情链接管理 ────────────────────────────────────────

def _validate_link_data(data, exclude_id=None):
    errors = {}
    name = (data.get('name') or '').strip()
    url = (data.get('url') or '').strip()
    description = (data.get('description') or '').strip()
    logo = (data.get('logo') or '').strip()

    if not name:
        errors['name'] = '请输入站点名称'
    elif len(name) > 50:
        errors['name'] = '名称为 1-50 个字符'

    if not url:
        errors['url'] = '请输入站点地址'
    elif len(url) > 200:
        errors['url'] = '地址不能超过 200 个字符'
    elif not url.startswith(('http://', 'https://')):
        errors['url'] = '请输入正确的 URL（需以 http:// 或 https:// 开头）'

    if len(description) > 200:
        errors['description'] = '描述不超过 200 个字符'
    if len(logo) > 255:
        errors['logo'] = 'Logo 地址不能超过 255 个字符'

    try:
        sort_order = max(int(data.get('sort_order', 0) or 0), 0)
    except (TypeError, ValueError):
        sort_order = 0

    if errors:
        return errors, None
    return None, {
        'name': name,
        'url': url,
        'description': description or None,
        'logo': logo or None,
        'sort_order': sort_order,
        'is_active': _parse_bool(data.get('is_active'), True),
    }


@api_bp.route('/admin/links', methods=['GET'])
@admin_required
def admin_link_list():
    links = Link.query.order_by(Link.sort_order.asc(), Link.created_at.desc()).all()
    return jsonify({'items': [link_to_dict(l) for l in links]})


@api_bp.route('/admin/links', methods=['POST'])
@admin_required
def admin_link_create():
    data = request.get_json(silent=True) or {}
    errors, cleaned = _validate_link_data(data)
    if errors:
        return jsonify({'success': False, 'message': '表单验证失败', 'errors': errors}), 400

    link = Link(**cleaned)
    db.session.add(link)
    db.session.commit()
    return jsonify({'success': True, 'message': '友链创建成功！', 'link': link_to_dict(link)}), 201


@api_bp.route('/admin/links/<int:link_id>', methods=['PUT'])
@admin_required
def admin_link_update(link_id):
    link = Link.query.get_or_404(link_id)
    data = request.get_json(silent=True) or {}
    errors, cleaned = _validate_link_data(data)
    if errors:
        return jsonify({'success': False, 'message': '表单验证失败', 'errors': errors}), 400

    for key, value in cleaned.items():
        setattr(link, key, value)
    db.session.commit()
    return jsonify({'success': True, 'message': '友链更新成功！', 'link': link_to_dict(link)})


@api_bp.route('/admin/links/<int:link_id>', methods=['DELETE'])
@admin_required
def admin_link_delete(link_id):
    link = Link.query.get_or_404(link_id)
    db.session.delete(link)
    db.session.commit()
    return jsonify({'success': True, 'message': '友链已删除'})


# ─── 评论/留言管理 ───────────────────────────────────────

@api_bp.route('/admin/comments', methods=['GET'])
@admin_required
def admin_comment_list():
    """评论列表（含文章标题，支持状态筛选）"""
    page, per_page = _get_page_params(default_per_page=20)
    status = request.args.get('status', 'all').strip()

    query = Comment.query
    if status == 'pending':
        query = query.filter_by(is_approved=False)
    elif status == 'approved':
        query = query.filter_by(is_approved=True)

    query = query.order_by(Comment.created_at.desc())
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    items = [
        {**comment_to_dict(c), 'post_title': c.post.title if c.post else '全站留言板'}
        for c in pagination.items
    ]
    return jsonify(pagination_to_dict(pagination, items))


@api_bp.route('/admin/comments/<int:comment_id>/approve', methods=['POST'])
@admin_required
def admin_comment_approve(comment_id):
    """审核通过/取消审核"""
    comment = Comment.query.get_or_404(comment_id)
    comment.is_approved = not comment.is_approved
    db.session.commit()
    status = '已审核' if comment.is_approved else '已取消审核'
    return jsonify({'success': True, 'message': f'评论 {status}', 'is_approved': comment.is_approved})


@api_bp.route('/admin/comments/<int:comment_id>', methods=['DELETE'])
@admin_required
def admin_comment_delete(comment_id):
    """删除评论（级联删除回复）"""
    comment = Comment.query.get_or_404(comment_id)
    db.session.delete(comment)
    db.session.commit()
    return jsonify({'success': True, 'message': '评论已删除'})


@api_bp.route('/admin/comments/<int:comment_id>/reply', methods=['POST'])
@admin_required
def admin_comment_reply(comment_id):
    """博主回复"""
    parent = Comment.query.get_or_404(comment_id)
    data = request.get_json(silent=True) or {}
    content = (data.get('content') or '').strip()

    if not content:
        return jsonify({'success': False, 'message': '请输入回复内容'}), 400
    if len(content) > 2000:
        return jsonify({'success': False, 'message': '回复内容为 1-2000 个字符'}), 400

    reply = Comment(
        post_id=parent.post_id,
        parent_id=comment_id,
        author_name=current_user.display_name,
        author_email=current_user.email,
        content=content,
        is_admin=True,
        is_approved=True,
        ip_address=get_client_ip(),
    )
    db.session.add(reply)
    db.session.commit()

    return jsonify({'success': True, 'message': '回复成功！', 'comment': comment_to_dict(reply)})


# ─── 个人资料 ────────────────────────────────────────────

@api_bp.route('/admin/profile', methods=['GET'])
@admin_required
def admin_profile_get():
    """获取当前用户资料"""
    return jsonify({'user': user_to_dict(current_user)})


@api_bp.route('/admin/profile', methods=['PUT'])
@admin_required
def admin_profile_update():
    """更新资料（昵称/邮箱/简介/头像路径）"""
    data = request.get_json(silent=True) or {}
    errors = {}

    nickname = (data.get('nickname') or '').strip()
    email = (data.get('email') or '').strip()
    bio = (data.get('bio') or '').strip()
    avatar = (data.get('avatar_path') or '').strip()

    if nickname and len(nickname) > 50:
        errors['nickname'] = '昵称不能超过 50 个字符'

    if not email:
        errors['email'] = '请输入邮箱'
    elif not _is_valid_email(email):
        errors['email'] = '邮箱格式不正确'
    elif User.query.filter(User.email == email, User.id != current_user.id).first():
        errors['email'] = '该邮箱已被使用'

    if len(bio) > 500:
        errors['bio'] = '简介不能超过 500 个字符'

    if errors:
        return jsonify({'success': False, 'message': '表单验证失败', 'errors': errors}), 400

    if nickname:
        current_user.nickname = nickname
    current_user.email = email
    current_user.bio = bio or None
    if avatar:
        current_user.avatar = avatar

    db.session.commit()
    return jsonify({'success': True, 'message': '个人资料更新成功！', 'user': user_to_dict(current_user)})


@api_bp.route('/admin/profile/password', methods=['POST'])
@admin_required
def admin_profile_password():
    """修改密码"""
    data = request.get_json(silent=True) or {}
    old_password = data.get('old_password') or ''
    new_password = data.get('new_password') or ''

    if not old_password:
        return jsonify({'success': False, 'message': '请输入当前密码'}), 400
    if not current_user.check_password(old_password):
        return jsonify({'success': False, 'message': '当前密码不正确'}), 400
    if len(new_password) < 6:
        return jsonify({'success': False, 'message': '新密码长度至少 6 位'}), 400

    current_user.set_password(new_password)
    db.session.commit()
    return jsonify({'success': True, 'message': '密码修改成功！下次登录请使用新密码'})
