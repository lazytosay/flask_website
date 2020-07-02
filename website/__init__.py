from flask import Flask, render_template
import click
import os
from website.settings import config
from website.extensions import bootstrap, db, ckeditor, moment, login_manager ,limiter
from website.blueprints.main import main_bp
from website.blueprints.auth import auth_bp


def create_app(config_name=None):
    app = Flask('website')

    if config_name is None:
        config_name = os.getenv('FLASK_CONFIG', 'production')

    app.config.from_object(config[config_name])

    register_blueprints(app)
    register_extensions(app)
    register_error_handlers(app)
    register_commands(app)
    register_shell_context(app)

    return app

def register_blueprints(app):
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, prefix="/auth")

def register_extensions(app):
    bootstrap.init_app(app)
    db.init_app(app)
    ckeditor.init_app(app)
    moment.init_app(app)
    login_manager.init_app(app)
    limiter.init_app(app)

def register_error_handlers(app):

    @app.errorhandler(429)
    def too_many_requests(e):
        return render_template("/errors/429.html", description=e.description), 429


def register_commands(app):
    @app.cli.command()
    def test():
        """test command"""
        click.echo("this is testing the command...")

    @app.cli.command()
    @click.option("--drop", is_flag=True, help="drop the tables")
    def initdb(drop):
        """initialize the database"""
        if drop:
            click.confirm("this will drop all the tables, are you sure? ", abort=True)
            db.drop_all()
            click.echo("dropped all the tables...")
        db.create_all()
        click.echo("Done...initialized the database")


def register_shell_context(app):
    @app.shell_context_processor
    def make_shell_context():
        return dict(db=db)