from flask import Flask,url_for,g,current_app
from flask_cors import CORS 
from flask_httpauth import HTTPBasicAuth,MultiAuth,HTTPTokenAuth
from flask_mail import Mail,Message
import utils

def create_app(config):
    app = Flask(__name__,static_folder="static",template_folder="templates")
    basic_auth = HTTPBasicAuth()
    token_auth = HTTPTokenAuth(scheme='Basic')
    cors=CORS()
    cors.init_app(app)
    app.config.from_pyfile(config)
    mail=Mail()
    mail.init_app(app)
    
    def close_db(e=None):
        db=g.pop("db",None)
        if db is not None:
            db.close()

    app.teardown_appcontext(close_db)

    import equity
    import auth
    import api
    import mutualfunds

    app.register_blueprint(equity.bp)
    app.register_blueprint(auth.bp)
    app.register_blueprint(api.bp)
    app.register_blueprint(mutualfunds.bp)

    #app.add_url_rule("/", endpoint="home")

    return app


