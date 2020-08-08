"""This module presents the app creation function exposed when importing the
module."""
import os
import code
import yaml
from .controller.authenticator import configure_authenticator
from flask import Flask, request
from .model.database import db, configure_database
from .model.facade import facade
from .model.sandbox import add_dummies_if_not_exist
from .view.ajax import ajax_blueprint
from .view.pages.diagram import diagram_blueprint
from .view.pages.information_page import info_blueprint
from .view.pages.error_page import error_blueprint
from .view.pages.report_result import result_report_blueprint


def create_app(config):
    """Create the flask app object.

    Args:
        config (dict): A dictionary containing the configuration values."""
    flask_app = Flask(__name__)
    if config['debug']:
        flask_app.config['DEBUG'] = True
        #app.config['SQLALCHEMY_ECHO'] = True
        print("Running in debug mode")
    else:
        print("Running in production mode")

    configure_database(flask_app, config)
    configure_authenticator(flask_app, config)

    if config['debug']:
        add_dummies_if_not_exist(flask_app)

    @flask_app.route('/')
    def root():
        return 'Root page'

    flask_app.register_blueprint(ajax_blueprint)
    flask_app.register_blueprint(diagram_blueprint)
    flask_app.register_blueprint(info_blueprint)
    flask_app.register_blueprint(error_blueprint)
    flask_app.register_blueprint(result_report_blueprint)

    return flask_app

def load_config():
    """Load the config file from 'config.ini'."""
    defaults = {
        'debug': False,
        'database-path': 'sqlite.db'
    }
    with open('config.yaml') as file:
        config = yaml.safe_load(file.read())
    
    for key, value in defaults.items():
        if key not in config:
            config[key] = str(value)
    
    return config

configuration = load_config()
app: Flask = create_app(configuration)
