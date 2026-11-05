from flask import *
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from werkzeug.datastructures import ImmutableOrderedMultiDict
from werkzeug.utils import secure_filename
import pytz
from pytz import timezone
import tzlocal
from sqlalchemy import exc
from flask_migrate import Migrate



def datetimefilter(value, format="%d/%m/%y %H:%M"):
    tz = pytz.timezone('Europe/Helsinki')
    utc = pytz.timezone('UTC')
    value = utc.localize(value, is_dst=None).astimezone(pytz.utc)
    local_dt = value.astimezone(tz)
    return local_dt.strftime(format)


class OrderedParamContainer(Request):
    parameter_storage_class = ImmutableOrderedMultiDict


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///flasktv.db'
app.config['SECRET_KEY'] = '7697e4d56cd537633a5ab239'
app.config['UPLOAD_FOLDER'] = './FlaskTV/static'
# Reload edited HTML templates even when Flask is started without debug mode.
app.config['TEMPLATES_AUTO_RELOAD'] = True
# app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.request_class = OrderedParamContainer
app.jinja_env.filters['datetimefilter'] = datetimefilter

db = SQLAlchemy(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)

# Routes import models, which need the initialized extensions above.
from FlaskTV import routes
