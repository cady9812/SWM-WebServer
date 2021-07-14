from flask import Blueprint, request, send_file
from app.models import Attack
from app import db, socketio
import os

bp = Blueprint('attack', __name__, url_prefix='/attack')

# 메인페이지
@bp.route('/')
def index():
    return "attack_views.py index function"

# 스캔 결과 받아서 공격 필터링
@bp.route('/show', methods=['GET', 'POST'])
def get_scan_result():
    if request.method == 'POST':
        try:
            scan_result = request.get_json() # 에이전트에서 보낸 포트 스캔 결과(json)
            filtered_attack = [] # 프론트로 보낼 db에 있는 공격들
            for result in scan_result:
                attacks = Attack.query.filter((Attack.program==result["service_product"])|(Attack.port==result["port"])).all()
                if attacks:
                    for attack in attacks:
                        filtered_attack.append({
                            "attackId":attack.attackId,
                            "program":attack.program,
                            "version":attack.version,
                            "port":attack.port,
                            "attackFileRoute":attack.attackFileRoute
                        })

            return { "status":200, "result" : filtered_attack }
            # return render_template('question/question_list.html', question_list=question_list)
            # templates 연동시 return 값 바꿔야 함.
        except Exception as e:
            print('/attack/show Error : ', e)
            return { "status":600, "result" : "공격 코드 필터링 server error"}
    else:
        return "attack_views.py get_scan_result function \"get\""


# # 공격 명령 내리기
# @bp.route('/execute')
# def order_attack():
#     # agent1 ip, agent2 ip, target ip
#     return "attack_views.py order_attack function"

# @socketio.on('connect', namespace='mynamespace')
# def order_attack():


# @socketio.on('myevent')
# def handle_my_event(json_data, methods=['GET','POST']):
    



# 공격 코드 다운받는 링크
@bp.route('/download/<string:attackId>/', methods=['GET'])
def download_attack_code(attackId):
    pwd = os.getcwd()
    file_name = f"{pwd}\\attack_files\\{attackId}.py" # 공격 파일 경로
    if os.path.isfile(file_name):
        return send_file(file_name,
                        mimetype='text/x-python',
                        attachment_filename=f"{attackId}.py",# 다운받아지는 파일 이름 -> 경로 지정할 수 있나?
                        as_attachment=True)
    else:
        return "wrong attackId"