import logging
from logging.handlers import SMTPHandler, RotatingFileHandler
import os
from config import Config
from flask import Flask, request, current_app
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_assets import Environment
from webassets import Bundle
from hanfor.utils.prefix_middleware import PrefixMiddleware

db = SQLAlchemy()
migrate = Migrate()


def register_assets(app):
    bundles = {
        'css': Bundle(
            'css/bootstrap.css',
            'css/bootstrap-grid.css',
            'css/bootstrap-reboot.css',
            'css/dataTables.bootstrap4.css',
            'css/select.bootstrap4.css',
            'css/tether.css',
            'css/jquery-ui.css',
            'css/bootstrap-tokenfield.css',
            'css/app.css',
            filters='cssutils',
            output='gen/style.css'
        )
    }

    assets = Environment(app)
    assets.register(bundles)


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)

    from hanfor.api import bp as api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    from hanfor.sites import bp as sites_bp
    app.register_blueprint(sites_bp, url_prefix='')

    if not app.testing:
        app.wsgi_app = PrefixMiddleware(app.wsgi_app, prefix=app.config['URL_PREFIX'])
        register_assets(app)

    if not app.debug:
        pass

    return app


from hanfor import models
