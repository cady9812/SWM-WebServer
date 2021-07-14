from flask import Blueprint, render_template

# from app.models import Question

#               이름    모듈명     url prefix
# 이름(main)은 나중에 함수명으로 url을 찾아주는 url_for 함수에서 사용할 예정 
bp = Blueprint('question', __name__, url_prefix='/question')

# @bp.route('/list/')
# def _list():
#     question_list = Question.query.order_by(Question.create_date.desc())
#     return render_template('question/question_list.html', question_list=question_list)

# @bp.route('/detail/<int:question_id>/')
# def detail(question_id):
#     question = Question.query.get_or_404(question_id)
#     return render_template('question/question_detail.html', question=question)