from flask import current_app, flash
from itsdangerous import BadSignature, SignatureExpired
from itsdangerous import TimedJSONWebSignatureSerializer as Serialier
from website.models import UserCommon as User
from website.extensions import db


def generate_token(username, operation, expire_in=None, **kwargs):
    s = Serialier(current_app.config['SECRET_KEY'], expire_in)
    data = {'id':username, 'operation': operation}
    data.update(**kwargs)
    return s.dumps(data)


def validate_token(username, token, operation):
    s = Serialier(current_app.config['SECRET_KEY'])

    try:
        data = s.loads(token)
    except (SignatureExpired, BadSignature):
        return False

    if operation != data.get('operation') or username != data.get('id'):
        return False

    if operation == "confirm":
        user = User.query.filter_by(username=username).first()
        user.confirmed = True
        db.session.commit()
        flash("done verifying...")

    return True

