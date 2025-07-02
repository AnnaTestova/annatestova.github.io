from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect

db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'your-super-secret-key'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db' 

    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    from .routes import app as main_app
    app.register_blueprint(main_app)

    return app
