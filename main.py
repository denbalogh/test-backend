import traceback

import sqlalchemy
from flask import Flask, request, g
from flask_cors import CORS
from flask_migrate import Migrate

import config
from util import converters
from database import db

# Define API base route
BASE_ROUTE = config.BASE_ROUTE

# Initialize flask app
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = config.DB_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config["SECRET_KEY"] = config.APP_SECRET

app.url_map.converters["str_list"] = converters.StringListConverter

CORS(app)
db.init_app(app)
Migrate(app, db)

# Import modules after app initialization to avoid circular references
from error import APIException, NotFoundError, MethodNotAllowedError
from util import auth
import util
import views.static
import views.user
import views.team

# Register API routes
app.register_blueprint(views.static.static, url_prefix=BASE_ROUTE + "/static")
app.register_blueprint(views.user.user, url_prefix=BASE_ROUTE + "/user")
app.register_blueprint(views.team.team, url_prefix=BASE_ROUTE + "/team")

# Global request handlers
@app.errorhandler(APIException)
def handle_error(error):
    """Catches exceptions and builds a corresponding error response"""
    return error.getResponse()


@app.errorhandler(sqlalchemy.orm.exc.NoResultFound)
def handle_sqlalchemy_notfound(error):
    return NotFoundError().getResponse()

@app.errorhandler(404)
def handle_404(error):
    return NotFoundError().getResponse()

@app.errorhandler(405)
def handle_405(error):
    return MethodNotAllowedError().getResponse()

@app.errorhandler(500)
def handle_500(error):
    if not config.DEBUG:
        message = "The service encountered an unforeseen server error."
    else:
        message = traceback.format_exc()
    return util.response(status_code=500, error_code=-1, error_message=message)

@app.before_request
def handle_authentication():
    """Handles authentication for every non-public API request"""
    if request.endpoint is None or getattr(app.view_functions[request.endpoint], "is_public", False) or request.blueprint == "google":
        return
    else:
        access_limit = getattr(app.view_functions[request.endpoint], "access_limit", None)
        auth.authenticate(access_limit=access_limit)

@app.after_request
def save_session_state(r):
    """Saves the current session state after each request to the redis database"""
    auth.save_session()
    return r

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
