import json
import logging
import psycopg2
from . import config
from flask_cors import CORS
from flask import Flask, make_response, g


def insurance_chat_api_app():
    app = Flask(__name__)
    app.config.from_object(config)
    app.logger.setLevel(logging.INFO)

    CORS(app)
    
    def get_db():
        if 'db' not in g:
            try:
                g.db = psycopg2.connect(
                    host=app.config['POSTGRES_HOST'],
                    database=app.config['POSTGRES_DB'],
                    user=app.config['POSTGRES_USER'], 
                    password=app.config['POSTGRES_PASSWORD'], 
                )
            except psycopg2.Error as e:
                app.logger.error("Database connection error: %s", e)
                raise
        return g.db

    @app.before_request
    def before_request():
        g.db = get_db()

    @app.teardown_request
    def teardown_request(exception):
        db = g.pop('db', None)
        if db is not None:
            db.close()

    @app.errorhandler(500)
    def internal_server_error(error):
        app.logger.exception('An exception occurred during a request.', error)
        return make_response(json.dumps({"status": "error", "message": "Internal Server Error"}), 200)

    @app.errorhandler(Exception)
    def unsupported_media_type(error):
        print(error)
        return make_response(json.dumps({"status": "error", "message": "Bad Request"}), 200)
            
    with app.app_context():
        from .controllers.controllers import bp_controllers
        app.register_blueprint(bp_controllers)

    return app