from flask import current_app, flash
from itsdangerous import BadSignature, SignatureExpired
from itsdangerous import TimedJSONWebSignatureSerializer as Serialier
from website.models import UserCommon as User
from website.extensions import db


def generate_token(username, operation, expire_in=900, **kwargs):
    s = Serialier(current_app.config['SECRET_KEY'], expire_in)
    data = {'id':username, 'operation': operation}
    data.update(**kwargs)
    return s.dumps(data)

def check_expiry(token):
    s = Serialier(current_app.config['SECRET_KEY'])
    try:
        data = s.loads(token)
    except (SignatureExpired, BadSignature):
        return False

    return True


def validate_token(username, token, operation):
    s = Serialier(current_app.config['SECRET_KEY'])

    try:
        data = s.loads(token)
    except (SignatureExpired, BadSignature):
        return False

    if operation != data.get('operation') or username != data.get('id'):
        return False

    user = User.query.filter_by(username=username).first_or_404()

    if operation == "confirm":
        user.is_confirmed = True
        db.session.commit()
        flash("done verifying...")

    elif operation == "reset-password":
        flash("token is valid, ready to reset your password...")
        return True

    else:
        flash("token failed to pass the verification, make sure it's not expired or the contents are not altered...")
        return False

    return True

