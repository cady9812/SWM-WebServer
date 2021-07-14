from flask import Blueprint, url_for
from werkzeug.utils import redirect

# from app.models import Question

#               이름    모듈명     url prefix
# 이름(main)은 나중에 함수명으로 url을 찾아주는 url_for 함수에서 사용할 예정 
bp = Blueprint('main', __name__, url_prefix='/')

@bp.route('/hello')
def hello_app(): # annotation과 매핑되는 함수 = 라우트 함수
    return "hello page!"

# @bp.route('/')
# def index():
#     #                       블루프린트이름.내부함수
#     return redirect(url_for('question._list'))
