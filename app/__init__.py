from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_cors import CORS

app = Flask(__name__)
app.config.from_object('config.DevConfig')

#Configuraciones
db = SQLAlchemy(app)
CORS(app,cors_allowed_origins="*")
migrate = Migrate(app,db)
login_manager = LoginManager(app)

# Blueprints
from app.models import  modelsBp
app.register_blueprint(modelsBp)

from app.post.main import postsBp
app.register_blueprint(postsBp)

from app.user.main import usersBp
app.register_blueprint(usersBp)

from app.action.main import actionsBp
app.register_blueprint(actionsBp)

from app.pagination.main import paginationsBp
app.register_blueprint(paginationsBp)

from app.popular.main import popularsBp
app.register_blueprint(popularsBp)

from app.recent.main import recentsBp
app.register_blueprint(recentsBp)

from app.sockets.chat import chatsBp
app.register_blueprint(chatsBp)
