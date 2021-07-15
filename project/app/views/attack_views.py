from flask import Blueprint, request, send_file
from flask.templating import render_template
from app.models import Attack
from app import db, agent_ip_dict, agent_ip_id
import os


bp = Blueprint('attack', __name__, url_prefix='/')

# 메인페이지
@bp.route('/')
def index():
    return render_template('index.html')

# 스캔 결과 받아서 공격 필터링
@bp.route('/scan-result', methods=['GET', 'POST'])
def get_scan_result():
    if request.method == 'POST':
        try:
            scan_result = request.get_json() # 에이전트에서 보낸 포트 스캔 결과(json)
            filtered_attack = [] # 프론트로 보낼 db에 있는 공격들
            for result in scan_result:
                #attacks = Attack.query.filter((Attack.program==result["service_product"])|(Attack.port==result["port"])).all()
                attacks = Attack.query.filter(Attack.program==result["service_product"]).all()
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


@bp.route('/cve/filter', methods=['GET', 'POST'])
def cve_filter():
    dst_ip = request.args.get('dst_ip') 
    # 에이전트 ip 리스트를 갖고있는 상태(에이전트와 서버 최초 연결시 에이전트가 보내줌)
    # 공격대상 == agent -> 보안장비 점검 -> 모든 cve list 출력
    # 공격대상 == target -> 웹 서버 점검 -> cve list 필터링

    


# 공격 명령 내리기
@bp.route('/command/<int:agentId>')
def order_attack():
    # agent1 ip, agent2 ip, target ip
    return 'r'


# # 연결되면 AGENT에서 IP 받기 -> agent ip list에 저장 -> agent에게 본인 id 알려주기
@bp.route('/agent/info', methods=['POST'])
def getAgentId():
    if request.method == 'POST':
        try:
            global agent_ip_dict
            global agent_ip_id
            getData = request.get_json()
            agentIP = getData["ip"]
            if agentIP not in agent_ip_dict.keys():
                agent_ip_id+=1
                agent_ip_dict[agentIP]=agent_ip_id
            return { "agent_id" : agent_ip_dict[agentIP] }
        except Exception as e:
            print('/agent/info Error : ', e)
            return
        




    

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