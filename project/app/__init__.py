from flask import Flask

from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

import config

# 변수는 create_app 밖에서 선언해야 한다.
db = SQLAlchemy()
migrate = Migrate()


# 애플리케이션 팩토리 사용
def create_app(): # create_app 함수가 애플리케이션 팩토리
    app = Flask(__name__)

    # config.py에 작성한 항목을 app.config 환경 변수로 부르기 위한 코드
    app.config.from_object(config)

    # ORM
    db.init_app(app)
    migrate.init_app(app, db)

    from . import models

    from .views import attack_views

    app.register_blueprint(attack_views.bp)
    #from .views import main_views, question_views

    #app.register_blueprint(main_views.bp)
    #app.register_blueprint(question_views.bp)

    return app
