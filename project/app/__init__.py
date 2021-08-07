from flask import Flask
from flask_redis import FlaskRedis
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from private import config

from app.modules import sckt_utils

MyIP = sckt_utils.get_local_ip()

db = SQLAlchemy()
migrate = Migrate()
redis_client = FlaskRedis()


# APPLICATION FACTORY
def create_app():
    app = Flask(__name__)

    app.config.from_object(config)


    # ORM
    db.init_app(app)
    migrate.init_app(app, db)

    # REDIS
    redis_client.init_app(app)
    
    from . import models

    # BLUEPRINT
    from .views import main_views, attack_views, agent_views, report_views
    app.register_blueprint(main_views.bp)
    app.register_blueprint(attack_views.bp)
    app.register_blueprint(agent_views.bp)
    app.register_blueprint(report_views.bp)

    return app

# def create_socket():
#     sckt.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#     while True:
#         try:
#             sckt.connect(('192.168.0.163', 9000))
#             break
#         except ConnectionRefusedError as e:
#             continue
#     return sckt