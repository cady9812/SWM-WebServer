from flask import Flask
from flask_redis import FlaskRedis
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from private import config

import socket


MyIP = socket.gethostbyname(socket.getfqdn())

# 변수는 create_app 밖에서 선언해야 한다.
db = SQLAlchemy()
migrate = Migrate()
redis_client = FlaskRedis()


# 애플리케이션 팩토리 사용
def create_app(): # create_app 함수가 애플리케이션 팩토리
    app = Flask(__name__)

    app.config.from_object(config)

    # ORM
    db.init_app(app)
    migrate.init_app(app, db)

    # redis
    redis_client.init_app(app)
    from . import models

    from .views import attack_views
    app.register_blueprint(attack_views.bp)


    return app
