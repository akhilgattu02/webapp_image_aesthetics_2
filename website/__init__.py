from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
from flask_mail import Mail
db = SQLAlchemy()
DB_NAME = "database.db"
mail = Mail()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'hjshjhdjah kjshkjdhjs'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    app.config['MAIL_SERVER']='smtp.gmail.com'            #appropriate email server
    app.config['MAIL_PORT'] = 587                         # appropriate mail port
    app.config['MAIL_USERNAME'] = ''  # add your email id
    app.config['MAIL_PASSWORD'] = ''         # add its password
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USE_SSL'] = False
    app.config['MAIL_DEFAULT_SENDER'] = ''       #add your email id
    db.init_app(app)
    mail.init_app(app)
    app.secret_key = "Dop89#$tcv"
   
    
    # from .run import run
    from .views import views
    from .auth import auth

    # app.register_blueprint(run, url_prefix='/survey')
    app.register_blueprint(auth, url_prefix='/')
    app.register_blueprint(views, url_prefix='/')

    from .models import User

    with app.app_context():
        db.create_all()

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app


def create_database(app):
    if not path.exists('website/' + DB_NAME):
        db.create_all(app=app)
        print('Created Database!')
