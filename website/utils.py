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


def validate_token(username, token, operation, new_password):
    s = Serialier(current_app.config['SECRET_KEY'])

    try:
        data = s.loads(token)
    except (SignatureExpired, BadSignature):
        return False

    if operation != data.get('operation') or username != data.get('id'):
        return False

    user = User.query.filter_by(username=username).first()
    if operation == "confirm":
        user.is_confirmed = True
        db.session.commit()
        flash("done verifying...")
    elif operation == "reset-password":
        if new_password:
            user.set_password(new_password)
            db.session.commit()
            flash("done changing your password...")
        else:
            flash("password received is empty...try again")

    else:
        flash("check failed: operation: ", data.get('operation'))

    return True

