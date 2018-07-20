import logging
from logging.handlers import SMTPHandler, RotatingFileHandler
import os
from config import Config
from flask import Flask, request, current_app
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_assets import Environment
from webassets import Bundle

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

    if not app.debug and not app.testing:
        register_assets(app)

    return app

from hanfor import models
