"""
后台管理路由 - 仅管理员可访问
包括仪表盘、文章管理、分类管理、标签管理、留言管理等
"""
import os
from datetime import datetime, date, timedelta

from flask import Blueprint, render_template, redirect, url_for, flash, request, \
    current_app, jsonify
from flask_login import login_required, current_user
from sqlalchemy import func

from app import db
from app.models.user import User
from app.models.post import Post
from app.models.category import Category
from app.models.tag import Tag
from app.models.comment import Comment
from app.models.link import Link
from app.models.site_stats import SiteStats
from app.models.post_tags import post_tags
from app.forms.post_form import PostForm, CategoryForm, TagForm
from app.forms.comment_form import CommentForm
from app.forms.link_form import LinkForm
from app.forms.profile_form import ProfileForm
from app.utils.decorators import admin_required
from app.utils.helpers import render_markdown, save_upload_image, save_avatar, \
    generate_slug, get_client_ip

admin_bp = Blueprint('admin', __name__, template_folder='../templates/admin')


# 所有后台路由都需要登录和管理员权限
@admin_bp.before_request
def require_admin():
    """后台路由前置拦截：确保已登录且是管理员"""
    if not current_user.is_authenticated:
        flash('请先登录', 'warning')
        return redirect(url_for('auth.login', next=request.url))
    if not current_user.is_admin:
        flash('无权限访问', 'danger')
        return redirect(url_for('front.index'))


# ─── 仪表盘 ──────────────────────────────────────────────


@admin_bp.route('/')
def dashboard():
    """
    后台仪表盘
    展示统计卡片和最近 7 天访问量趋势
    """
    # 统计数据
    post_count = Post.query.count()
    category_count = Category.query.count()
    tag_count = Tag.query.count()
    comment_count = Comment.query.count()
    pending_comments = Comment.query.filter_by(is_approved=False).count()

    # 最近 7 天访问量（转换为可序列化格式）
    recent_stats_raw = SiteStats.get_recent_days(7)
    recent_stats = [
        {'date': s.date.strftime('%Y-%m-%d'), 'pv': s.pv, 'uv': s.uv}
        for s in recent_stats_raw
    ]

    # 最新文章
    recent_posts = Post.query.order_by(Post.created_at.desc()).limit(5).all()

    # 最新留言
    recent_comments = Comment.query.order_by(Comment.created_at.desc()).limit(5).all()

    # 总访问量
    total_stats = SiteStats.get_total_stats()

    return render_template(
        'admin/dashboard.html',
        post_count=post_count,
        category_count=category_count,
        tag_count=tag_count,
        comment_count=comment_count,
        pending_comments=pending_comments,
        recent_stats=recent_stats,
        recent_posts=recent_posts,
        recent_comments=recent_comments,
        total_stats=total_stats
    )


# ─── 文章管理 ────────────────────────────────────────────


@admin_bp.route('/posts')
def post_list():
    """
    文章列表
    支持按标题搜索、按分类筛选
    """
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '').strip()
    category_id = request.args.get('category_id', type=int)

    query = Post.query

    # 搜索
    if search:
        query = query.filter(Post.title.contains(search))

    # 分类筛选
    if category_id:
        query = query.filter_by(category_id=category_id)

    # 排序
    query = query.order_by(Post.is_top.desc(), Post.created_at.desc())

    pagination = query.paginate(page=page, per_page=15, error_out=False)
    posts = pagination.items

    categories = Category.query.order_by(Category.name).all()

    return render_template(
        'admin/post_list.html',
        posts=posts,
        pagination=pagination,
        categories=categories,
        search=search,
        category_id=category_id
    )


@admin_bp.route('/posts/create', methods=['GET', 'POST'])
def post_create():
    """
    新增文章
    """
    form = PostForm()

    if form.validate_on_submit():
        post = Post()
        # 手动赋值（避免 populate_obj 把 tags 字符串赋给关系字段）
        tags_input = (form.tags.data or '').strip()
        post.title = form.title.data
        post.slug = form.slug.data
        post.summary = form.summary.data
        post.content = form.content.data
        post.category_id = form.category_id.data if form.category_id.data and form.category_id.data != 0 else None
        post.is_published = form.is_published.data
        post.is_top = form.is_top.data
        post.allow_comment = form.allow_comment.data

        # 处理封面图片上传
        if form.cover_image.data:
            try:
                cover_path = save_upload_image(
                    form.cover_image.data,
                    folder='covers'
                )
                post.cover_image = cover_path
            except Exception as e:
                flash(f'封面图片上传失败: {str(e)}', 'warning')

        # 设置作者
        post.author_id = current_user.id

        # 设置发布时间
        if post.is_published and not post.published_at:
            post.published_at = datetime.now()

        # 生成内容 HTML 缓存
        if post.content:
            post.content_html = render_markdown(post.content)

        db.session.add(post)
        db.session.commit()

        # 处理标签
        if tags_input:
            tag_names = [t.strip() for t in tags_input.split(',') if t.strip()]
            _process_post_tags(post, tag_names)

        db.session.commit()

        flash('文章创建成功！', 'success')
        return redirect(url_for('admin.post_list'))

    return render_template('admin/post_edit.html', form=form, is_edit=False)


@admin_bp.route('/posts/edit/<int:post_id>', methods=['GET', 'POST'])
def post_edit(post_id):
    """
    编辑文章
    """
    post = Post.query.get_or_404(post_id)
    form = PostForm(obj=post)

    # 预填标签
    if request.method == 'GET' and post.tags:
        form.tags.data = ', '.join([tag.name for tag in post.tags])

    if form.validate_on_submit():
        # 手动赋值（避免 populate_obj 把 tags 字符串赋给关系字段）
        tags_input = (form.tags.data or '').strip()
        post.title = form.title.data
        post.slug = form.slug.data
        post.summary = form.summary.data
        post.content = form.content.data
        post.category_id = form.category_id.data if form.category_id.data and form.category_id.data != 0 else None
        post.is_published = form.is_published.data
        post.is_top = form.is_top.data
        post.allow_comment = form.allow_comment.data

        # 处理封面图片
        if form.cover_image.data:
            try:
                cover_path = save_upload_image(
                    form.cover_image.data,
                    folder='covers'
                )
                post.cover_image = cover_path
            except Exception as e:
                flash(f'封面图片上传失败: {str(e)}', 'warning')

        # 设置发布时间
        if post.is_published and not post.published_at:
            post.published_at = datetime.now()

        # 更新 HTML 缓存
        if post.content:
            post.content_html = render_markdown(post.content)

        # 处理标签
        tag_names = [t.strip() for t in tags_input.split(',') if t.strip()]
        _process_post_tags(post, tag_names)

        db.session.commit()
        flash('文章更新成功！', 'success')
        return redirect(url_for('admin.post_list'))

    return render_template('admin/post_edit.html', form=form, post=post, is_edit=True)


@admin_bp.route('/posts/delete/<int:post_id>', methods=['POST'])
def post_delete(post_id):
    """
    删除文章
    """
    post = Post.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    flash('文章已删除', 'success')
    return redirect(url_for('admin.post_list'))


@admin_bp.route('/posts/batch-delete', methods=['POST'])
def post_batch_delete():
    """
    批量删除文章
    """
    post_ids = request.form.getlist('post_ids', type=int)
    if not post_ids:
        flash('请选择要删除的文章', 'warning')
        return redirect(url_for('admin.post_list'))

    Post.query.filter(Post.id.in_(post_ids)).delete(synchronize_session=False)
    db.session.commit()
    flash(f'已删除 {len(post_ids)} 篇文章', 'success')
    return redirect(url_for('admin.post_list'))


@admin_bp.route('/posts/toggle-top/<int:post_id>', methods=['POST'])
def post_toggle_top(post_id):
    """切换文章置顶状态"""
    post = Post.query.get_or_404(post_id)
    post.is_top = not post.is_top
    db.session.commit()
    return jsonify({'success': True, 'is_top': post.is_top})


@admin_bp.route('/posts/toggle-publish/<int:post_id>', methods=['POST'])
def post_toggle_publish(post_id):
    """切换文章发布状态"""
    post = Post.query.get_or_404(post_id)
    post.is_published = not post.is_published
    if post.is_published and not post.published_at:
        post.published_at = datetime.now()
    db.session.commit()
    return jsonify({'success': True, 'is_published': post.is_published})


# ─── 分类管理 ────────────────────────────────────────────


@admin_bp.route('/categories')
def category_list():
    """分类列表"""
    categories = Category.query.order_by(Category.post_count.desc()).all()
    return render_template('admin/category_list.html', categories=categories)


@admin_bp.route('/categories/create', methods=['GET', 'POST'])
def category_create():
    """新增分类"""
    form = CategoryForm()
    if form.validate_on_submit():
        category = Category(
            name=form.name.data.strip(),
            slug=form.slug.data.strip(),
            description=form.description.data.strip() if form.description.data else None
        )
        db.session.add(category)
        db.session.commit()
        flash('分类创建成功！', 'success')
        return redirect(url_for('admin.category_list'))
    return render_template('admin/category_edit.html', form=form, is_edit=False)


@admin_bp.route('/categories/edit/<int:category_id>', methods=['GET', 'POST'])
def category_edit(category_id):
    """编辑分类"""
    category = Category.query.get_or_404(category_id)
    form = CategoryForm(obj=category)
    if form.validate_on_submit():
        form.populate_obj(category)
        db.session.commit()
        flash('分类更新成功！', 'success')
        return redirect(url_for('admin.category_list'))
    return render_template('admin/category_edit.html', form=form, category=category, is_edit=True)


@admin_bp.route('/categories/delete/<int:category_id>', methods=['POST'])
def category_delete(category_id):
    """删除分类"""
    category = Category.query.get_or_404(category_id)
    # 检查是否有文章关联
    if category.post_count > 0:
        flash(f'分类 "{category.name}" 下有 {category.post_count} 篇文章，无法删除', 'danger')
    else:
        db.session.delete(category)
        db.session.commit()
        flash('分类已删除', 'success')
    return redirect(url_for('admin.category_list'))


# ─── 标签管理 ────────────────────────────────────────────


@admin_bp.route('/tags')
def tag_list():
    """标签列表"""
    tags = Tag.query.order_by(Tag.post_count.desc()).all()
    return render_template('admin/tag_list.html', tags=tags)


@admin_bp.route('/tags/create', methods=['GET', 'POST'])
def tag_create():
    """新增标签"""
    form = TagForm()
    if form.validate_on_submit():
        tag = Tag(
            name=form.name.data.strip(),
            slug=form.slug.data.strip()
        )
        db.session.add(tag)
        db.session.commit()
        flash('标签创建成功！', 'success')
        return redirect(url_for('admin.tag_list'))
    return render_template('admin/tag_edit.html', form=form, is_edit=False)


@admin_bp.route('/tags/edit/<int:tag_id>', methods=['GET', 'POST'])
def tag_edit(tag_id):
    """编辑标签"""
    tag = Tag.query.get_or_404(tag_id)
    form = TagForm(obj=tag)
    if form.validate_on_submit():
        form.populate_obj(tag)
        db.session.commit()
        flash('标签更新成功！', 'success')
        return redirect(url_for('admin.tag_list'))
    return render_template('admin/tag_edit.html', form=form, tag=tag, is_edit=True)


@admin_bp.route('/tags/delete/<int:tag_id>', methods=['POST'])
def tag_delete(tag_id):
    """删除标签"""
    tag = Tag.query.get_or_404(tag_id)
    db.session.delete(tag)
    db.session.commit()
    flash('标签已删除', 'success')
    return redirect(url_for('admin.tag_list'))


# ─── 留言管理 ────────────────────────────────────────────


@admin_bp.route('/comments')
def comment_list():
    """留言列表"""
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status', 'all')

    query = Comment.query
    if status == 'pending':
        query = query.filter_by(is_approved=False)
    elif status == 'approved':
        query = query.filter_by(is_approved=True)

    query = query.order_by(Comment.created_at.desc())
    pagination = query.paginate(page=page, per_page=20, error_out=False)
    comments = pagination.items

    return render_template('admin/comment_list.html', comments=comments, pagination=pagination, status=status)


@admin_bp.route('/comments/approve/<int:comment_id>', methods=['POST'])
def comment_approve(comment_id):
    """审核通过留言"""
    comment = Comment.query.get_or_404(comment_id)
    comment.is_approved = not comment.is_approved
    db.session.commit()
    status = '已审核' if comment.is_approved else '已取消审核'
    flash(f'评论 {status}', 'success')
    return redirect(url_for('admin.comment_list'))


@admin_bp.route('/comments/delete/<int:comment_id>', methods=['POST'])
def comment_delete(comment_id):
    """删除留言"""
    comment = Comment.query.get_or_404(comment_id)
    db.session.delete(comment)
    db.session.commit()
    flash('评论已删除', 'success')
    return redirect(url_for('admin.comment_list'))


@admin_bp.route('/comments/reply/<int:comment_id>', methods=['POST'])
def comment_reply(comment_id):
    """回复留言（博主回复）"""
    parent_comment = Comment.query.get_or_404(comment_id)
    content = request.form.get('content', '').strip()

    if not content:
        flash('请输入回复内容', 'warning')
        return redirect(url_for('admin.comment_list'))

    reply = Comment(
        post_id=parent_comment.post_id,
        parent_id=comment_id,
        author_name=current_user.display_name,
        author_email=current_user.email,
        content=content,
        is_admin=True,
        is_approved=True,
        ip_address=get_client_ip()
    )
    db.session.add(reply)
    db.session.commit()

    flash('回复成功！', 'success')
    return redirect(url_for('admin.comment_list'))


# ─── 友情链接管理 ───────────────────────────────────────


@admin_bp.route('/links')
def link_list():
    """友链列表"""
    links = Link.query.order_by(Link.sort_order.asc(), Link.created_at.desc()).all()
    return render_template('admin/link_list.html', links=links)


@admin_bp.route('/links/create', methods=['GET', 'POST'])
def link_create():
    """新增友链"""
    form = LinkForm()
    if form.validate_on_submit():
        link = Link()
        form.populate_obj(link)
        db.session.add(link)
        db.session.commit()
        flash('友链创建成功！', 'success')
        return redirect(url_for('admin.link_list'))
    return render_template('admin/link_edit.html', form=form, is_edit=False)


@admin_bp.route('/links/edit/<int:link_id>', methods=['GET', 'POST'])
def link_edit(link_id):
    """编辑友链"""
    link = Link.query.get_or_404(link_id)
    form = LinkForm(obj=link)
    if form.validate_on_submit():
        form.populate_obj(link)
        db.session.commit()
        flash('友链更新成功！', 'success')
        return redirect(url_for('admin.link_list'))
    return render_template('admin/link_edit.html', form=form, link=link, is_edit=True)


@admin_bp.route('/links/delete/<int:link_id>', methods=['POST'])
def link_delete(link_id):
    """删除友链"""
    link = Link.query.get_or_404(link_id)
    db.session.delete(link)
    db.session.commit()
    flash('友链已删除', 'success')
    return redirect(url_for('admin.link_list'))


# ─── 个人设置 ────────────────────────────────────────────


@admin_bp.route('/profile', methods=['GET', 'POST'])
def profile():
    """个人资料编辑 + 密码修改"""
    form = ProfileForm(obj=current_user)

    if form.validate_on_submit():
        # 判断是修改资料还是修改密码
        if form.change_password.data and form.old_password.data:
            # 修改密码
            if not current_user.check_password(form.old_password.data):
                flash('当前密码不正确', 'danger')
                return redirect(url_for('admin.profile'))
            current_user.set_password(form.new_password.data)
            db.session.commit()
            flash('密码修改成功！下次登录请使用新密码', 'success')
            return redirect(url_for('admin.profile'))
        else:
            # 更新昵称
            if form.nickname.data:
                current_user.nickname = form.nickname.data.strip()

            # 更新邮箱
            current_user.email = form.email.data.strip()

            # 更新简介
            if form.bio.data:
                current_user.bio = form.bio.data.strip()

            # 处理头像上传
            if form.avatar.data:
                try:
                    avatar_path = save_avatar(form.avatar.data)
                    current_user.avatar = avatar_path
                    flash('头像上传成功！', 'success')
                except Exception as e:
                    flash(f'头像上传失败: {str(e)}', 'danger')

            db.session.commit()
            flash('个人资料更新成功！', 'success')
            return redirect(url_for('admin.profile'))

    return render_template('admin/profile.html', form=form)


# ─── 辅助函数 ────────────────────────────────────────────


def _process_post_tags(post, tag_names):
    """
    处理文章的标签关联
    创建不存在的标签，更新计数

    :param post: Post 对象
    :param tag_names: 标签名称列表
    """
    tags = []
    for name in tag_names:
        # 查找或创建标签
        tag = Tag.query.filter_by(name=name).first()
        if not tag:
            slug = generate_slug(name)
            # 确保 slug 唯一
            base_slug = slug
            counter = 1
            while Tag.query.filter_by(slug=slug).first():
                slug = f'{base_slug}-{counter}'
                counter += 1

            tag = Tag(name=name, slug=slug)
            db.session.add(tag)
            db.session.flush()  # 立即获取 ID
        tags.append(tag)

    # 更新关联
    post.tags = tags

    # 更新所有标签的文章计数
    for tag in tags:
        tag.update_post_count()
