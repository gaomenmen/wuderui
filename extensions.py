from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_babel import Babel
from flask_migrate import Migrate

db = SQLAlchemy()
login_manager = LoginManager()
babel = Babel()
migrate = Migrate()

login_manager.login_view = 'auth.login'
login_manager.login_message = None
