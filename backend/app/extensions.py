"""Extension singletons. Created here (unbound) so any module can import them
without causing circular imports; they are bound to the app in create_app()."""
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
jwt = JWTManager()
cors = CORS()
