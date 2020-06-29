from flask import Flask
import os
from website.settings import config
from website.extensions import bootstrap, limiter


def create_app(config_name=None):
    app = Flask('website')

    if config_name is None:
        config_name = os.getenv('FLASK_CONFIG', 'production')

    app.config.from_object(config[config_name])

    register_blueprints(app)
    register_extensions(app)

    return app

def register_blueprints(app):
    from website.blueprints.main import main_bp
    app.register_blueprint(main_bp)

def register_extensions(app):
    bootstrap.init_app(app)
    limiter.init_app(app)
