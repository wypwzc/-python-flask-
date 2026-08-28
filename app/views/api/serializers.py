"""
API 序列化器 - 将 ORM 模型转换为前端可消费的 JSON 结构
统一的 datetime 输出格式：%Y-%m-%dT%H:%M:%S（JS Date 可直接解析）
"""
from flask import url_for


def _dt_to_str(dt):
    """datetime → 字符串，None 返回 None"""
    if dt is None:
        return None
    return dt.strftime('%Y-%m-%dT%H:%M:%S')


def _media_url(path):
    """相对上传路径（uploads/...）→ 完整 URL"""
    if not path:
        return None
    return url_for('static', filename=path)


def post_to_dict(post, include_content=False):
    """
    文章 → dict
    :param include_content: 是否包含 Markdown 原文（仅编辑接口使用）
    """
    data = {
        'id': post.id,
        'title': post.title,
        'slug': post.slug,
        'summary': post.summary,
        'cover_image': _media_url(post.cover_image),
        'cover_image_path': post.cover_image,
        'tags': [tag.name for tag in post.tags],
        'category': {
            'id': post.category.id,
            'name': post.category.name,
            'slug': post.category.slug
        } if post.category else None,
        'views': post.views or 0,
        'likes': post.likes or 0,
        'is_published': post.is_published,
        'is_top': post.is_top,
        'allow_comment': post.allow_comment,
        'content_html': post.content_html,
        'published_at': _dt_to_str(post.published_at),
        'created_at': _dt_to_str(post.created_at),
        'updated_at': _dt_to_str(post.updated_at),
    }
    if include_content:
        data['content'] = post.content
    return data


def comment_to_dict(comment):
    """评论/留言 → dict"""
    return {
        'id': comment.id,
        'post_id': comment.post_id,
        'parent_id': comment.parent_id,
        'author_name': comment.author_name,
        'author_email': comment.author_email,
        'author_url': comment.author_url,
        'content': comment.content,
        'is_admin': comment.is_admin,
        'is_approved': comment.is_approved,
        'created_at': _dt_to_str(comment.created_at),
    }


def category_to_dict(category):
    """分类 → dict"""
    return {
        'id': category.id,
        'name': category.name,
        'slug': category.slug,
        'description': category.description,
        'post_count': category.post_count or 0,
        'created_at': _dt_to_str(category.created_at),
    }


def tag_to_dict(tag):
    """标签 → dict"""
    return {
        'id': tag.id,
        'name': tag.name,
        'slug': tag.slug,
        'post_count': tag.post_count or 0,
        'created_at': _dt_to_str(tag.created_at),
    }


def link_to_dict(link):
    """友链 → dict"""
    return {
        'id': link.id,
        'name': link.name,
        'url': link.url,
        'description': link.description,
        'logo': _media_url(link.logo),
        'sort_order': link.sort_order or 0,
        'is_active': link.is_active,
        'created_at': _dt_to_str(link.created_at),
    }


def user_to_dict(user):
    """用户 → dict"""
    return {
        'id': user.id,
        'username': user.username,
        'nickname': user.nickname,
        'display_name': user.display_name,
        'email': user.email,
        'bio': user.bio,
        'avatar': _media_url(user.avatar),
        'avatar_path': user.avatar,
        'is_admin': user.is_admin,
        'last_login': _dt_to_str(user.last_login),
        'created_at': _dt_to_str(user.created_at),
    }


def pagination_to_dict(pagination, items):
    """Flask-SQLAlchemy Pagination → 统一分页结构"""
    return {
        'total': pagination.total,
        'pages': pagination.pages,
        'has_prev': pagination.has_prev,
        'has_next': pagination.has_next,
        'page': pagination.page,
        'per_page': pagination.per_page,
        'items': items,
    }
