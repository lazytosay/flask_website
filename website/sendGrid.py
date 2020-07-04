from website.extensions import sendgrid_client
from sendgrid.helpers.mail import Mail
from threading import Thread
from website.models import UserCommon as User
from flask import abort, flash, render_template

def _send_async_email(message):
    sendgrid_client.send(message)


def send_email(from_email, to_email, subject, template, **kwargs):
    mail = Mail(
        from_email=from_email,
        to_emails=to_email,
        subject=subject,
        plain_text_content= render_template(template + '.txt', **kwargs),
        html_content = render_template(template + '.html', **kwargs)
    )

    t = Thread(target=_send_async_email, args=[mail])
    t.start()
    return t

def send_confirm_email(token, username):
    user = User.query.filter_by(username=username).first()
    if not user:
        flash("send_confirm_email: user not found")
        abort(404)
    send_email(
        from_email='noreply@xyzdatabase.com',
        to_email=user.email,
        subject="confirm your account",
        template='emails/confirm',
        username=username,
        token=token
    )

def send_reset_password_email(token, username):
    user = User.query.filter_by(username=username).first()
    if not user:
        flash("forget password email: user not found")
        abort(404)

    send_email(
        from_email='noreply@xyzdatabase.com',
        to_email=user.email,
        subject="confirm your account",
        template='emails/reset_password',
        username=username,
        token=token
    )