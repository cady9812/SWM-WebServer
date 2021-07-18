from typing import Pattern
from flask import Blueprint, request, send_file
from flask.templating import render_template
from app.models import Attack
# from app import db, agent_ip_dict, agent_ip_id, command_json
from app import db, redis_client
import os


bp = Blueprint('attack', __name__, url_prefix='/')

# # 메인페이지
# @bp.route('/')
# def index():
#     return render_template('index.html')

# # 스캔 결과 받아서 공격 필터링
# @bp.route('/scan-result', methods=['GET', 'POST'])
# def get_scan_result():
#     if request.method == 'POST':
#         try:
#             scan_result = request.get_json() # 에이전트에서 보낸 포트 스캔 결과(json)
#             filtered_attack = [] # 프론트로 보낼 db에 있는 공격들
#             for result in scan_result:
#                 #attacks = Attack.query.filter((Attack.program==result["service_product"])|(Attack.port==result["port"])).all()
#                 attacks = Attack.query.filter(Attack.program==result["service_product"]).all()
#                 if attacks:
#                     for attack in attacks:
#                         filtered_attack.append({
#                             "attackId":attack.attackId,
#                             "program":attack.program,
#                             "version":attack.version,
#                             "port":attack.port,
#                             "fileName":attack.fileName,
#                             "usage":attack.usage
#                         })

#             return { "status":200, "result" : filtered_attack }
#             # return render_template('question/question_list.html', question_list=question_list)
#             # templates 연동시 return 값 바꿔야 함.
#         except Exception as e:
#             print('/scan-result Error : ', e)
#             return { "status":600, "result" : "공격 코드 필터링 server error"}
#     else:
#         return "attack_views.py get_scan_result function \"get\""

# # nextCVE 버튼 클릭했을때
# @bp.route('/cve/filter')
# def nextCVEButtonClicked():
#     global command_json, agent_ip_dict
#     # 에이전트 ip 리스트를 갖고있는 상태(에이전트와 서버 최초 연결시 에이전트가 보내줌)
#     # 공격대상 == agent -> 보안장비 점검 -> 모든 cve list 출력
#     # 공격대상 == target -> 웹 서버 점검 -> cve list 필터링
#     dst_ip = request.args.get('dst_ip')
#     src_ip = request.args.get('src_ip')
#     command_json[agent_ip_dict[dst_ip]]={
#         "type":"scan",
#         "ip":dst_ip
#     }
#     """
#     command_json = {
#         0: {
#             "type":"scan",
#             "ip":"127.0.0.1"
#         },
#         1: {

#         }
#     }
#     """
#1231231231
# # attackStart 버튼 클릭했을때
# @bp.route('/attack/start')
# def attackStartButtonClicked():
#     global command_json, agent_ip_dict
#     # 프론트에서 받을 변수
#     src_ip = ""
#     dst_ip = ""
#     attackIdx = "" # -> target_port, usage, attackName
#     ################
#     attackInfo = Attack.query.filter(Attack.attackId==attackIdx).first()
#     attackName = attackInfo.fileName
#     target_port = attackInfo.port
#     usage = attackInfo.usage
#     download = f"http://172.30.1.9:5000/download/{attackName}"
#     command_json[agent_ip_dict[src_ip]]={
#             "type":"attack",
#             "download": download,
#             "target_ip": dst_ip,
#             "target_port": target_port,
#             "usage": usage
#     }
#testest123123123
# @bp.route('/command/<int:agentId>')
# def commandToAgent(agentId):
#     global command_json
#     if agentId in command_json:
#         return command_json.pop(agentId, None)
#     else:
#         return {
#             "type":"no command"
#         }

# # # 연결되면 AGENT에서 IP 받기 -> agent ip list에 저장 -> agent에게 본인 id 알려주기
# @bp.route('/agent/info', methods=['POST'])
# def getAgentId():
#     if request.method == 'POST':
#         try:
#             global agent_ip_dict
#             global agent_ip_id
#             getData = request.get_json()
#             agentIP = getData["ip"]
#             if agentIP not in agent_ip_dict.keys():
#                 agent_ip_id+=1
#                 agent_ip_dict[agentIP]=agent_ip_id
#             return { "agent_id" : agent_ip_dict[agentIP] }
#         except Exception as e:
#             print('/agent/info Error : ', e)
#             return
# 
# # 공격 코드 다운받는 링크
# @bp.route('/download/<string:attackName>/', methods=['GET'])
# def download_attack_code(attackName):
#     pwd = os.getcwd()
#     file_name = f"{pwd}\\attack_files\\{attackName}.py" # 공격 파일 경로
#     if os.path.isfile(file_name):
#         return send_file(file_name,
#                         mimetype='text/x-python',
#                         attachment_filename=f"{attackName}.py",# 다운받아지는 파일 이름 -> 경로 지정할 수 있나?
#                         as_attachment=True)
#     else:
#         return "wrong attackName"
# 
##########################################################################################
########## Redis 변경 ################

        

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
                            "fileName":attack.fileName,
                            "usage":attack.usage
                        })

            return { "status":200, "result" : filtered_attack }
            # return render_template('question/question_list.html', question_list=question_list)
            # templates 연동시 return 값 바꿔야 함.
        except Exception as e:
            print('/scan-result Error : ', e)
            return { "status":600, "result" : "공격 코드 필터링 server error"}
    else:
        return "attack_views.py get_scan_result function \"get\""

# agent가 자신 ip 알려주기
@bp.route('/agent/info', methods=['POST'])
def getAgentId():
    if request.method == 'POST':
        try:
            getData = request.get_json()
            agentIP = getData["ip"]
            redis_n = int(redis_client.get('n').decode())
            if redis_client.hget('agent_ip_list', agentIP) == None: # 아직 저장하지 않은 ip라면
                redis_n += 1
                redis_client.hset('agent_ip_list', agentIP, str(redis_n)) # agent_ip_list에 {ip : n} 추가
                redis_client.set('n', str(redis_n)) # n update
            redis_agent_id = redis_client.hget('agent_ip_list', agentIP).decode()
            return {
                "agent_id" : redis_agent_id
            }
        except Exception as e:
            print('/agent/info Error : ', e)
            return

# nextCVE 버튼 클릭시 
@bp.route('/cve/filter')
def nextCVEButtonClicked():
    try:   
        # ❌ target 버튼이 체크되어있을 때만 -> 구현해야 함
        src_ip = request.args.get('src_ip')
        dst_ip = request.args.get('dst_ip')
        # src_ip에게 dst_ip를 포트스캔하라 명령 저장
        if redis_client.hget('agent_ip_list', src_ip) == None:
            return "this src_ip is not stored in Redis"
        src_ip_n = int(redis_client.hget('agent_ip_list', src_ip).decode())
        redis_client.hmset(f'command{src_ip_n}', {
            "type":"scan",
            "ip":dst_ip
        })
        comm = redis_client.hgetall(f'command{src_ip_n}')
        comm = { key.decode(): val.decode() for key, val in comm.items() }
        #print(comm)
        return comm
    except Exception as e:
        print('/cve/filter Error : ', e)
        return {
            "status":"600"
        }

# attackStart 버튼 클릭 시 
@bp.route('/attack/start')
def attackStartButtonClicked():
    # ❌ 프론트에 맞춰 구현해야 함.
    src_ip = "127.0.0.1" # 프론트에서 받을 변수
    # src_ip = ""
    dst_ip = "10.10.10.10" # 프론트에서 받을 변수
    # dst_ip = ""
    attackIdx = 1 # 변수로 바꿔야 함프론트에서 받을 변수(공격 코드 번호) -> can get target_port, usage, attackName by attackIdx
    ###################
    
    if redis_client.hget('agent_ip_list', src_ip) == None: # src는 무조건 agent, dst는 agent일 수도 target일 수도
        return "this src_ip or dst_ip is not stored in Redis"

    src_ip_n = int(redis_client.hget('agent_ip_list', src_ip).decode())

    redis_all_keys = redis_client.keys("*")
    redis_all_keys = [ i.decode() for i in redis_all_keys]
    if f"command{src_ip_n}" in redis_all_keys:
        redis_client.delete(f"command{src_ip_n}")


    attackInfo = Attack.query.filter(Attack.attackId==attackIdx).first()
    attackName = attackInfo.fileName

    redis_client.hmset(f'command{src_ip_n}', {
        "type":"attack",
        "download": f"http://172.30.1.9:5000/download/{attackName}",
        "target_ip": dst_ip,
        "target_port": attackInfo.port,
        "usage": attackInfo.usage
    })

    comm = redis_client.hgetall(f'command{src_ip_n}')
    comm = { key.decode(): val.decode() for key, val in comm.items() }
    # print(comm)
    return comm

@bp.route('/command/<int:agentId>')
def commandToAgent(agentId):
    redis_all_keys = redis_client.keys("*")
    redis_all_keys = [ i.decode() for i in redis_all_keys]
    if f"command{agentId}" in redis_all_keys:
        comm = redis_client.hgetall(f'command{agentId}')
        comm = { key.decode(): val.decode() for key, val in comm.items() }
        return comm
    else:
        return {
            "type":"no command"
        }
        


# 공격 코드 다운받는 링크
@bp.route('/download/<string:attackName>/', methods=['GET'])
def download_attack_code(attackName):
    pwd = os.getcwd()
    file_name = f"{pwd}\\attack_files\\{attackName}.py" # 공격 파일 경로
    if os.path.isfile(file_name):
        return send_file(file_name,
                        mimetype='text/x-python',
                        attachment_filename=f"{attackName}.py",# 다운받아지는 파일 이름 -> 경로 지정할 수 있나?
                        as_attachment=True)
    else:
        return "wrong attackName"