"""
前台路由 - 博客前端页面
包括首页、文章详情、分类、标签、关于、归档、搜索、友情链接等
"""
from flask import Blueprint, render_template, request, abort, jsonify, session, current_app
from app import db
from app.models.post import Post
from app.models.category import Category
from app.models.tag import Tag
from app.models.comment import Comment
from app.models.link import Link
from app.models.site_stats import SiteStats
from app.models.post_like import PostLike
from app.forms.comment_form import CommentForm, MessageForm
from app.utils.helpers import render_markdown, get_client_ip, truncate_text
from app.utils.decorators import comment_rate_limit, sensitive_words_filter
from sqlalchemy import func, or_
from datetime import datetime, date

front_bp = Blueprint('front', __name__)


@front_bp.before_request
def record_visitor():
    """请求前置处理 - 记录访客信息（仅记录页面访问）"""
    # 只记录 GET 请求
    if request.method != 'GET':
        return

    # 排除静态文件和后台请求
    if request.path.startswith('/static') or request.path.startswith('/admin') or request.path.startswith('/auth'):
        return

    try:
        # 简单的 PV 统计（每 60 秒内同一 IP 只算一次）
        today = date.today()
        ip = get_client_ip()
        stats_key = f'stats_{today}_{ip}'

        if not session.get(stats_key):
            stats = SiteStats.query.filter_by(date=today).first()
            if not stats:
                stats = SiteStats(date=today, pv=0, uv=0, ip_count=0)
                db.session.add(stats)

            stats.pv = (stats.pv or 0) + 1

            # UV 统计（基于 Session）
            uv_key = f'uv_{today}'
            if not session.get(uv_key):
                stats.uv = (stats.uv or 0) + 1
                session[uv_key] = True

            db.session.commit()
            session[stats_key] = True
            session.permanent = True
    except Exception as e:
        # 统计失败不应影响正常访问
        current_app.logger.error(f'统计记录失败: {str(e)}')


# ─── 首页 ────────────────────────────────────────────────


@front_bp.route('/')
def index():
    """
    博客首页
    展示文章列表（置顶文章优先），支持分页
    """
    page = request.args.get('page', 1, type=int)
    category_slug = request.args.get('category')

    # 构建查询
    query = Post.query.filter_by(is_published=True)

    # 分类筛选
    if category_slug:
        category = Category.query.filter_by(slug=category_slug).first_or_404()
        query = query.filter_by(category_id=category.id)

    # 排序：置顶优先，再按发布时间倒序
    query = query.order_by(Post.is_top.desc(), Post.published_at.desc())

    # 分页查询
    pagination = query.paginate(
        page=page,
        per_page=current_app.config.get('POSTS_PER_PAGE', 10),
        error_out=True
    )
    posts = pagination.items

    return render_template(
        'front/index.html',
        posts=posts,
        pagination=pagination,
        category_slug=category_slug
    )


# ─── 文章详情 ────────────────────────────────────────────


@front_bp.route('/post/<slug>')
def post_detail(slug):
    """
    文章详情页
    渲染 Markdown 内容，记录阅读量（Session 防刷）
    """
    post = Post.query.filter_by(slug=slug, is_published=True).first_or_404()

    # 阅读量统计（使用 Session 防刷）
    viewed_key = f'viewed_post_{post.id}'
    if not session.get(viewed_key):
        post.increment_views()
        session[viewed_key] = True

    # 渲染 Markdown（优先使用缓存的 content_html）
    if post.content_html:
        content_html = post.content_html
    else:
        content_html = render_markdown(post.content)
        post.content_html = content_html
        db.session.commit()

    # 获取上一篇和下一篇（按发布时间）
    prev_post = Post.query.filter(
        Post.is_published == True,
        Post.published_at < post.published_at
    ).order_by(Post.published_at.desc()).first()

    next_post = Post.query.filter(
        Post.is_published == True,
        Post.published_at > post.published_at
    ).order_by(Post.published_at.asc()).first()

    # 相关文章（基于相同标签，排除当前文章）
    related_posts = []
    if post.tags:
        tag_ids = [tag.id for tag in post.tags]
        related_posts = Post.query.filter(
            Post.is_published == True,
            Post.id != post.id,
            Post.tags.any(Tag.id.in_(tag_ids))
        ).order_by(Post.views.desc()).limit(5).all()

    # 评论表单
    form = CommentForm()
    message_form = MessageForm()

    # 获取已审核的评论（不含嵌套回复的一级评论）
    comments = Comment.query.filter_by(
        post_id=post.id,
        parent_id=None,
        is_approved=True
    ).order_by(Comment.created_at.asc()).all()

    # 加载每层回复
    for comment in comments:
        comment.replies_list = Comment.query.filter_by(
            parent_id=comment.id,
            is_approved=True
        ).order_by(Comment.created_at.asc()).all()

    return render_template(
        'front/post_detail.html',
        post=post,
        content_html=content_html,
        prev_post=prev_post,
        next_post=next_post,
        related_posts=related_posts,
        comments=comments,
        form=form,
        message_form=message_form
    )


# ─── 分类 ────────────────────────────────────────────────


@front_bp.route('/category/<slug>')
def category_detail(slug):
    """
    分类页面
    展示该分类下的所有文章，支持分页
    """
    category = Category.query.filter_by(slug=slug).first_or_404()

    page = request.args.get('page', 1, type=int)
    pagination = Post.query.filter_by(
        is_published=True,
        category_id=category.id
    ).order_by(
        Post.is_top.desc(),
        Post.published_at.desc()
    ).paginate(
        page=page,
        per_page=current_app.config.get('POSTS_PER_PAGE', 10),
        error_out=True
    )
    posts = pagination.items

    return render_template(
        'front/category.html',
        category=category,
        posts=posts,
        pagination=pagination
    )


# ─── 标签 ────────────────────────────────────────────────


@front_bp.route('/tag/<slug>')
def tag_detail(slug):
    """
    标签页面
    展示该标签下的所有文章，支持分页
    """
    tag = Tag.query.filter_by(slug=slug).first_or_404()

    page = request.args.get('page', 1, type=int)
    pagination = tag.posts.filter_by(
        is_published=True
    ).order_by(
        Post.is_top.desc(),
        Post.published_at.desc()
    ).paginate(
        page=page,
        per_page=current_app.config.get('POSTS_PER_PAGE', 10),
        error_out=True
    )
    posts = pagination.items

    return render_template(
        'front/tag.html',
        tag=tag,
        posts=posts,
        pagination=pagination
    )


# ─── 关于页面 ────────────────────────────────────────────


@front_bp.route('/about')
def about():
    """
    关于页面
    展示博主信息（内容可在后台编辑）
    """
    # 获取管理员用户
    from app.models.user import User
    admin = User.query.filter_by(is_admin=True).first()
    post_count = Post.query.filter_by(is_published=True).count()
    category_count = Category.query.count()
    tag_count = Tag.query.count()
    return render_template(
        'front/about.html',
        admin=admin,
        post_count=post_count,
        category_count=category_count,
        tag_count=tag_count
    )


# ─── 归档页面 ────────────────────────────────────────────


@front_bp.route('/archive')
def archive():
    """
    文章归档页面
    按年份/月份分组展示文章，时间轴样式
    """
    from sqlalchemy import extract

    # 查询所有已发布的文章
    posts = Post.query.filter_by(is_published=True)\
        .order_by(Post.published_at.desc()).all()

    # 按年份/月份分组
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
                    'posts': []
                }
            archives[year][month]['count'] += 1
            archives[year][month]['posts'].append(post)

    # 按年份倒序排列
    archives = dict(sorted(archives.items(), reverse=True))

    return render_template('front/archive.html', archives=archives)


# ─── 友情链接页面 ────────────────────────────────────────


@front_bp.route('/links')
def links():
    """
    友情链接页面
    展示所有启用的友链
    """
    links = Link.query.filter_by(is_active=True)\
        .order_by(Link.sort_order.asc(), Link.created_at.desc()).all()
    return render_template('front/links.html', links=links)


# ─── 留言板页面 ──────────────────────────────────────────


@front_bp.route('/message', methods=['GET', 'POST'])
def message():
    """
    全站留言板
    访客无需登录即可留言
    """
    form = MessageForm()

    if form.validate_on_submit():
        # 创建留言
        comment = Comment(
            post_id=None,  # NULL 表示全站留言
            author_name=form.author_name.data.strip(),
            author_email=form.author_email.data.strip(),
            content=form.content.data.strip(),
            ip_address=get_client_ip(),
            user_agent=request.user_agent.string[:255] if request.user_agent else None,
            is_approved=True,
            is_admin=False
        )
        db.session.add(comment)
        db.session.commit()
        return jsonify({'success': True, 'message': '留言发布成功！'})

    # 获取已审核的留言
    page = request.args.get('page', 1, type=int)
    pagination = Comment.query.filter_by(
        post_id=None,
        parent_id=None,
        is_approved=True
    ).order_by(
        Comment.created_at.desc()
    ).paginate(page=page, per_page=20, error_out=False)

    comments = pagination.items
    # 加载回复
    for comment in comments:
        comment.replies_list = Comment.query.filter_by(
            parent_id=comment.id,
            is_approved=True
        ).order_by(Comment.created_at.asc()).all()

    return render_template(
        'front/message.html',
        comments=comments,
        pagination=pagination,
        form=form
    )


# ─── 搜索 ────────────────────────────────────────────────


@front_bp.route('/search')
def search():
    """
    全文搜索页面
    使用 MySQL LIKE 查询（生产环境建议改为 FULLTEXT 索引）
    """
    q = request.args.get('q', '').strip()
    page = request.args.get('page', 1, type=int)

    if not q:
        return render_template('front/search.html', posts=[], query=q, pagination=None)

    # 使用 LIKE 进行全文搜索
    search_term = f'%{q}%'
    pagination = Post.query.filter(
        Post.is_published == True,
        or_(
            Post.title.like(search_term),
            Post.content.like(search_term),
            Post.summary.like(search_term)
        )
    ).order_by(
        Post.is_top.desc(),
        Post.published_at.desc()
    ).paginate(page=page, per_page=10, error_out=False)

    posts = pagination.items

    return render_template(
        'front/search.html',
        posts=posts,
        query=q,
        pagination=pagination
    )


# ─── AJAX 接口 ───────────────────────────────────────────


@front_bp.route('/post/<slug>/like', methods=['POST'])
def like_post(slug):
    """
    文章点赞（AJAX）
    基于 IP 限制每人每篇文章只能点赞一次
    """
    post = Post.query.filter_by(slug=slug).first_or_404()
    ip = get_client_ip()

    # 检查是否已点赞
    existing = PostLike.query.filter_by(post_id=post.id, ip_address=ip).first()
    if existing:
        return jsonify({'success': False, 'message': '您已经赞过了', 'likes': post.likes})

    # 记录点赞
    like = PostLike(
        post_id=post.id,
        ip_address=ip,
        user_agent=request.user_agent.string[:255] if request.user_agent else None
    )
    db.session.add(like)
    post.likes = (post.likes or 0) + 1
    db.session.commit()

    return jsonify({'success': True, 'message': '点赞成功！', 'likes': post.likes})


@front_bp.route('/post/<slug>/comment', methods=['POST'])
@comment_rate_limit
@sensitive_words_filter
def post_comment(slug):
    """
    提交文章评论（AJAX）
    """
    post = Post.query.filter_by(slug=slug).first_or_404()

    if not post.allow_comment:
        return jsonify({'success': False, 'message': '该文章已关闭评论'})

    form = CommentForm()
    if form.validate_on_submit():
        parent_id = request.form.get('parent_id', type=int)

        comment = Comment(
            post_id=post.id,
            parent_id=parent_id,
            author_name=form.author_name.data.strip(),
            author_email=form.author_email.data.strip(),
            author_url=form.author_url.data.strip() or None,
            content=form.content.data.strip(),
            ip_address=get_client_ip(),
            user_agent=request.user_agent.string[:255] if request.user_agent else None,
            is_approved=True,
            is_admin=False
        )
        db.session.add(comment)
        db.session.commit()

        # 发送邮件通知博主
        try:
            from app.utils.email import send_comment_notification
            send_comment_notification(comment)
        except Exception as e:
            current_app.logger.error(f'发送评论通知失败: {e}')

        return jsonify({
            'success': True,
            'message': '评论发布成功！',
            'comment': {
                'id': comment.id,
                'author_name': comment.author_name,
                'content': comment.content,
                'created_at': comment.created_at.strftime('%Y-%m-%d %H:%M'),
                'is_admin': comment.is_admin
            }
        })

    # 表单验证失败
    errors = {field: errors for field, errors in form.errors.items()}
    return jsonify({'success': False, 'message': '表单验证失败', 'errors': errors})
