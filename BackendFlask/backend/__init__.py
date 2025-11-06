from flask import Flask
from .extensions import db, migrate, jwt
from .config import Config

# Import blueprint
from .iot.routes import iot_bp
from .children.routes import children_bp
from .auth.routes import auth_bp
from .dashboard.routes import dashboard_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Init extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    # Register blueprints
    app.register_blueprint(iot_bp, url_prefix="/iot")
    app.register_blueprint(children_bp, url_prefix="/children")
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(dashboard_bp, url_prefix="/dashboard")

    print("DB URI:", app.config["SQLALCHEMY_DATABASE_URI"])

    return app
