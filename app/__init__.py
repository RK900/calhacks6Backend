import logging
import os

from flask import Flask, render_template
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from app.config import config, Config

db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()
cors = CORS()
logger = logging.getLogger(__name__)


def create_app(config_name=None, db_ref=None) -> Flask:
    if not config_name:
        config_name = os.getenv('FLASK_ENV', 'development')
    app = Flask(__name__)
    app_config = config[config_name]
    app.config.from_object(app_config)

    if db_ref is None:
        db.init_app(app)
        db.reflect(app=app)
        migrate.init_app(app, db)
    else:
        db_ref.init_app(app)
        db_ref.reflect(app=app)
        migrate.init_app(app, db_ref)

    with app.app_context():
        db.create_all()

    bcrypt.init_app(app)
    cors.init_app(app)

    configure_blueprints(app)
    configure_error_handlers(app)
    return app


def configure_blueprints(flask_app: Flask):
    from app.main import main
    flask_app.register_blueprint(main)


def configure_error_handlers(app):
    @app.errorhandler(404)
    def page_not_found(error):
        return render_template("errors/404.html"), 404
