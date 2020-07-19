# coding=utf-8

import os

from flask import Flask
from flask_admin import Admin, AdminIndexView
from flask_admin import helpers as admin_helpers
from flask_security import Security
from flask_security.datastore import SQLAlchemyUserDatastore

from application.admin import *
from application.models import *
from application.utils import db


def get_config_file():
    return os.getenv('FLASK_CONFIG_FILE') or 'config.py'


def init_database(database_file):
    app_dir = os.path.realpath(os.path.dirname(__file__))
    database_path = os.path.join(app_dir, database_file)
    if os.path.exists(database_path):
        return

    print(database_path + " not exists")
    db.drop_all()
    db.create_all()
    db.session.commit()
    print("create table success")

    user_role = Role(name='user', description='用户组')
    administrator_role = Role(name='administrator', description='管理员组')
    db.session.add(user_role)
    db.session.add(administrator_role)
    db.session.commit()
    print("create roles success")

    user = User(
        username='admin',
        email='admin',
        password=hash_password('admin'),
        active=True,
        roles=[user_role, administrator_role]
    )
    db.session.add(user)
    db.session.commit()
    print("create default admin user success")


def create_app():
    flask_app = Flask(__name__)
    flask_app.config.from_pyfile(get_config_file())

    db.init_app(flask_app)

    flask_admin = Admin(flask_app, name=flask_app.config['ADMIN_NAME'],
                        base_template='my_master.html',
                        template_mode="bootstrap3",
                        index_view=AdminIndexView(name='首页', menu_icon_type='glyph', menu_icon_value='glyphicon-home'))
    flask_admin.add_view(
        UserView(User, db.session, name='用户', menu_icon_type='glyph', menu_icon_value='glyphicon-user'))
    flask_admin.add_view(
        RoleView(Role, db.session, name='角色', menu_icon_type='glyph', menu_icon_value='glyphicon-lock'))

    user_datastore = SQLAlchemyUserDatastore(db, User, Role)
    security = Security(flask_app, datastore=user_datastore)

    @security.context_processor
    def security_context_processor():
        return dict(
            admin_base_template=flask_admin.base_template,
            admin_view=flask_admin.index_view,
            h=admin_helpers, get_url=url_for)

    with flask_app.app_context():
        init_database(flask_app.config['DATABASE_FILE'])

    from application.home import home_bp
    flask_app.register_blueprint(home_bp, url_prefix='/')

    return flask_app


__all__ = ["create_app"]
