"""
邮件发送工具模块
使用 Flask-Mail 异步发送通知邮件
"""
from threading import Thread
from flask import current_app, render_template
from flask_mail import Message
from app import mail


def send_async_email(app, msg):
    """
    异步发送邮件（在后台线程中执行）

    :param app: Flask 应用实例
    :param msg: Message 对象
    """
    with app.app_context():
        try:
            mail.send(msg)
        except Exception as e:
            current_app.logger.error(f'邮件发送失败: {str(e)}')


def send_email(subject, recipients, template, **kwargs):
    """
    发送邮件通用函数

    :param subject: 邮件主题
    :param recipients: 收件人列表
    :param template: 邮件模板名称（不含 .html）
    :param kwargs: 模板变量
    """
    app = current_app._get_current_object()
    msg = Message(
        subject=subject,
        recipients=recipients if isinstance(recipients, list) else [recipients]
    )
    msg.body = render_template(f'email/{template}.txt', **kwargs)
    msg.html = render_template(f'email/{template}.html', **kwargs)

    # 异步发送
    thread = Thread(target=send_async_email, args=(app, msg))
    thread.daemon = True
    thread.start()


def send_comment_notification(comment):
    """
    发送新评论通知邮件给博主

    :param comment: Comment 对象
    """
    admin_email = current_app.config.get('ADMIN_EMAIL', '')
    if not admin_email:
        return

    post_title = comment.post.title if comment.post else '全站留言板'
    send_email(
        subject=f'博客新评论 - {post_title}',
        recipients=[admin_email],
        template='comment_notification',
        comment=comment,
        post_title=post_title
    )


def send_reply_notification(comment, reply):
    """
    发送回复通知邮件给原评论者

    :param comment: 原评论对象
    :param reply: 回复评论对象
    """
    if not comment.author_email:
        return

    send_email(
        subject=f'您的评论收到了回复 - {reply.author_name}',
        recipients=[comment.author_email],
        template='reply_notification',
        comment=comment,
        reply=reply
    )
