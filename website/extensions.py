from flask_bootstrap import Bootstrap
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

bootstrap = Bootstrap()
limiter = Limiter(key_func=get_remote_address, default_limits=["500 per day", "120 per hour"])