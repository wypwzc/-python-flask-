"""
前台 API - 博客公开数据接口
文章列表/详情、分类、标签、归档、搜索、友链、留言板、点赞、评论、PV 统计
"""
from datetime import date

from flask import jsonify, request, session, current_app
from flask_login import login_required, current_user
from sqlalchemy import or_

from app import db
from app.models.post import Post
from app.models.category import Category
from app.models.tag import Tag
from app.models.comment import Comment
from app.models.link import Link
from app.models.site_stats import SiteStats
from app.models.post_like import PostLike
from app.utils.helpers import get_client_ip
from app.utils.decorators import comment_rate_limit, sensitive_words_filter
from app.views.api import api_bp
from app.views.api.serializers import (
    post_to_dict, comment_to_dict, category_to_dict, tag_to_dict,
    link_to_dict, pagination_to_dict,
)


# ─── 通用工具 ────────────────────────────────────────────

def _get_page_params(default_per_page=10, max_per_page=50):
    """解析并钳制分页参数"""
    page = request.args.get('page', 1, type=int) or 1
    per_page = request.args.get('per_page', default_per_page, type=int) or default_per_page
    page = max(page, 1)
    per_page = min(max(per_page, 1), max_per_page)
    return page, per_page


def _clean_comment_content(data):
    """清洗评论/留言内容，返回内容字符串或错误消息"""
    content = (data.get('content') or '').strip()
    if not content:
        return None, '请输入内容'
    if len(content) > 2000:
        return None, '内容为 1-2000 个字符'
    return content, None


def _record_visitor():
    """PV/UV 统计（IP + 60 秒去重，与原 before_request 逻辑一致）"""
    try:
        today = date.today()
        ip = get_client_ip()
        stats_key = f'stats_{today}_{ip}'

        if not session.get(stats_key):
            stats = SiteStats.query.filter_by(date=today).first()
            if not stats:
                stats = SiteStats(date=today, pv=0, uv=0, ip_count=0)
                db.session.add(stats)

            stats.pv = (stats.pv or 0) + 1

            uv_key = f'uv_{today}'
            if not session.get(uv_key):
                stats.uv = (stats.uv or 0) + 1
                session[uv_key] = True

            db.session.commit()
            session[stats_key] = True
            session.permanent = True
    except Exception as e:
        current_app.logger.error(f'统计记录失败: {str(e)}')


# ─── 文章 ────────────────────────────────────────────────

@api_bp.route('/posts', methods=['GET'])
@login_required
def post_list():
    """
    文章列表（首页/分类/标签/搜索共用）
    query: page, per_page, category(slug), tag(slug), q(搜索关键词)
    """
    page, per_page = _get_page_params()
    category_slug = request.args.get('category')
    tag_slug = request.args.get('tag')
    q = (request.args.get('q') or '').strip()

    query = Post.query.filter_by(is_published=True)

    if category_slug:
        category = Category.query.filter_by(slug=category_slug).first_or_404()
        query = query.filter_by(category_id=category.id)

    if tag_slug:
        tag = Tag.query.filter_by(slug=tag_slug).first_or_404()
        query = query.filter(Post.tags.any(Tag.id == tag.id))

    if q:
        search_term = f'%{q}%'
        query = query.filter(or_(
            Post.title.like(search_term),
            Post.content.like(search_term),
            Post.summary.like(search_term),
        ))

    query = query.order_by(Post.is_top.desc(), Post.published_at.desc())
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    items = [post_to_dict(p) for p in pagination.items]
    return jsonify(pagination_to_dict(pagination, items))


@api_bp.route('/posts/<slug>', methods=['GET'])
@login_required
def post_detail(slug):
    """
    文章详情
    返回 content_html（服务端 Markdown 渲染）、上一篇/下一篇、相关文章、点赞状态
    """
    post = Post.query.filter_by(slug=slug, is_published=True).first_or_404()

    # 阅读量统计（Session 防刷）
    viewed_key = f'viewed_post_{post.id}'
    if not session.get(viewed_key):
        post.views = (post.views or 0) + 1
        db.session.commit()
        session[viewed_key] = True

    # 上一篇/下一篇（按发布时间，未发布时间的文章跳过）
    prev_post = next_post = None
    if post.published_at:
        prev_post = Post.query.filter(
            Post.is_published == True,  # noqa: E712
            Post.published_at < post.published_at
        ).order_by(Post.published_at.desc()).first()

        next_post = Post.query.filter(
            Post.is_published == True,  # noqa: E712
            Post.published_at > post.published_at
        ).order_by(Post.published_at.asc()).first()

    # 相关文章（相同标签，排除当前文章）
    related_posts = []
    if post.tags:
        tag_ids = [tag.id for tag in post.tags]
        related_posts = Post.query.filter(
            Post.is_published == True,  # noqa: E712
            Post.id != post.id,
            Post.tags.any(Tag.id.in_(tag_ids))
        ).order_by(Post.views.desc()).limit(5).all()

    # 当前 IP 是否已点赞
    ip = get_client_ip()
    is_liked = PostLike.query.filter_by(post_id=post.id, ip_address=ip).first() is not None

    return jsonify({
        'post': post_to_dict(post),
        'prev_post': post_to_dict(prev_post) if prev_post else None,
        'next_post': post_to_dict(next_post) if next_post else None,
        'related_posts': [post_to_dict(p) for p in related_posts],
        'is_liked': is_liked,
    })


@api_bp.route('/posts/<slug>/like', methods=['POST'])
@login_required
def like_post(slug):
    """文章点赞（IP 去重，每 IP 每文一次）"""
    post = Post.query.filter_by(slug=slug).first_or_404()
    ip = get_client_ip()

    existing = PostLike.query.filter_by(post_id=post.id, ip_address=ip).first()
    if existing:
        return jsonify({'success': False, 'message': '您已经赞过了', 'likes': post.likes, 'liked': True})

    like = PostLike(
        post_id=post.id,
        ip_address=ip,
        user_agent=request.user_agent.string[:255] if request.user_agent else None
    )
    db.session.add(like)
    post.likes = (post.likes or 0) + 1
    db.session.commit()

    return jsonify({'success': True, 'message': '点赞成功！', 'likes': post.likes, 'liked': True})


@api_bp.route('/posts/<slug>/comment', methods=['POST'])
@login_required
@comment_rate_limit
@sensitive_words_filter
def post_comment(slug):
    """提交文章评论（登录用户，支持 parent_id 嵌套回复）"""
    post = Post.query.filter_by(slug=slug).first_or_404()

    if not post.allow_comment:
        return jsonify({'success': False, 'message': '该文章已关闭评论'}), 400

    data = request.get_json(silent=True) or {}
    content, error = _clean_comment_content(data)
    if error:
        return jsonify({'success': False, 'message': error}), 400

    raw_parent_id = data.get('parent_id')
    parent_id = int(raw_parent_id) if str(raw_parent_id).isdigit() and int(raw_parent_id) > 0 else None
    if parent_id:
        parent = Comment.query.filter_by(id=parent_id, post_id=post.id).first()
        if not parent:
            return jsonify({'success': False, 'message': '回复的评论不存在'}), 400

    comment = Comment(
        post_id=post.id,
        parent_id=parent_id,
        author_name=current_user.display_name,
        author_email=current_user.email or '',
        author_url=None,
        content=content,
        ip_address=get_client_ip(),
        user_agent=request.user_agent.string[:255] if request.user_agent else None,
        is_approved=True,
        is_admin=current_user.is_admin
    )
    db.session.add(comment)
    db.session.commit()

    # 邮件通知
    try:
        from app.utils.email import send_comment_notification, send_reply_notification
        send_comment_notification(comment)
        if parent_id:
            send_reply_notification(parent, comment)
    except Exception as e:
        current_app.logger.error(f'发送评论通知失败: {e}')

    return jsonify({
        'success': True,
        'message': '评论发布成功！',
        'comment': comment_to_dict(comment),
    })


# ─── 评论与留言 ──────────────────────────────────────────

@api_bp.route('/comments', methods=['GET'])
@login_required
def comment_list():
    """
    评论列表（平铺，前端组树）
    query: post_id(省略则为留言板), page, per_page
    """
    page, per_page = _get_page_params(default_per_page=20)
    post_id = request.args.get('post_id', type=int)

    query = Comment.query.filter_by(is_approved=True)
    if post_id is not None:
        query = query.filter_by(post_id=post_id)
    else:
        query = query.filter_by(post_id=None)

    query = query.order_by(Comment.created_at.asc())
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    items = [comment_to_dict(c) for c in pagination.items]
    return jsonify(pagination_to_dict(pagination, items))


@api_bp.route('/messages', methods=['GET'])
@login_required
def message_list():
    """留言板列表（一级留言，分页，按时间倒序）"""
    page, _ = _get_page_params(default_per_page=20)
    query = Comment.query.filter_by(post_id=None, parent_id=None, is_approved=True) \
        .order_by(Comment.created_at.desc())
    pagination = query.paginate(page=page, per_page=20, error_out=False)
    items = [comment_to_dict(c) for c in pagination.items]
    return jsonify(pagination_to_dict(pagination, items))


@api_bp.route('/messages', methods=['POST'])
@login_required
@comment_rate_limit
@sensitive_words_filter
def message_submit():
    """提交留言（登录用户）"""
    data = request.get_json(silent=True) or {}
    content, error = _clean_comment_content(data)
    if error:
        return jsonify({'success': False, 'message': error}), 400

    comment = Comment(
        post_id=None,
        parent_id=None,
        author_name=current_user.display_name,
        author_email=current_user.email or '',
        content=content,
        ip_address=get_client_ip(),
        user_agent=request.user_agent.string[:255] if request.user_agent else None,
        is_approved=True,
        is_admin=current_user.is_admin
    )
    db.session.add(comment)
    db.session.commit()

    try:
        from app.utils.email import send_comment_notification
        send_comment_notification(comment)
    except Exception as e:
        current_app.logger.error(f'发送留言通知失败: {e}')

    return jsonify({'success': True, 'message': '留言发布成功！', 'comment': comment_to_dict(comment)})


# ─── 分类 / 标签 / 友链 ──────────────────────────────────

@api_bp.route('/categories', methods=['GET'])
@login_required
def category_list():
    """分类列表"""
    categories = Category.query.order_by(Category.post_count.desc(), Category.name).all()
    return jsonify({'items': [category_to_dict(c) for c in categories]})


@api_bp.route('/tags', methods=['GET'])
@login_required
def tag_list():
    """标签列表"""
    tags = Tag.query.order_by(Tag.post_count.desc(), Tag.name).all()
    return jsonify({'items': [tag_to_dict(t) for t in tags]})


@api_bp.route('/links', methods=['GET'])
@login_required
def link_list():
    """友情链接（仅启用）"""
    links = Link.query.filter_by(is_active=True) \
        .order_by(Link.sort_order.asc(), Link.created_at.desc()).all()
    return jsonify({'items': [link_to_dict(l) for l in links]})


# ─── 归档 / 侧边栏 / PV 统计 ─────────────────────────────

@api_bp.route('/archive', methods=['GET'])
@login_required
def archive():
    """文章归档（按年份/月份分组，年份倒序）"""
    from sqlalchemy import extract

    posts = Post.query.filter_by(is_published=True) \
        .order_by(Post.published_at.desc()).all()

    archives = {}
    for post in posts:
        if post.published_at:
            year = post.published_at.year
            month = post.published_at.month
            if year not in archives:
                archives[year] = {}
            if month not in archives[year]:
                archives[year][month] = {
                    'month_name': post.published_at.strftime('%B'),
                    'count': 0,
                    'posts': [],
                }
            archives[year][month]['count'] += 1
            archives[year][month]['posts'].append(post_to_dict(post))

    archives = dict(sorted(archives.items(), reverse=True))
    return jsonify({'archives': archives})


@api_bp.route('/sidebar', methods=['GET'])
@login_required
def sidebar():
    """侧边栏聚合数据（替代原 context_processor 注入的全局变量）"""
    categories = Category.query.order_by(Category.post_count.desc()).all()
    recent_posts = Post.query.filter_by(is_published=True) \
        .order_by(Post.published_at.desc()).limit(5).all()
    recent_comments = Comment.query.filter_by(is_approved=True) \
        .order_by(Comment.created_at.desc()).limit(5).all()
    total_stats = SiteStats.get_total_stats()

    from app.models.user import User
    blog_admin = User.query.filter_by(is_admin=True).first()

    from app.views.api.serializers import user_to_dict
    return jsonify({
        'categories': [category_to_dict(c) for c in categories],
        'recent_posts': [post_to_dict(p) for p in recent_posts],
        'recent_comments': [comment_to_dict(c) for c in recent_comments],
        'total_stats': total_stats,
        'blog_admin': user_to_dict(blog_admin) if blog_admin else None,
    })


@api_bp.route('/pv', methods=['POST'])
def record_pv():
    """PV/UV 统计（SPA 路由切换时 fire-and-forget 调用）"""
    _record_visitor()
    return jsonify({'success': True})
