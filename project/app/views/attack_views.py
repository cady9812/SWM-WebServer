from flask import Blueprint, request, send_file
from flask.templating import render_template
import time

from app.models import Attack
from app import redis_client, MyIP, db

import os

from app.modules import crawler


<<<<<<< HEAD
#         }
#     }
#     """
#123123123133
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
=======
bp = Blueprint('attack', __name__, url_prefix='/')

>>>>>>> 0ea9ce2f1d047a16f8a81a3afd1385e6a57d88fe



# 메인페이지
@bp.route('/')
def index():
    # redis_client.flushdb()
    # redis_client.set("n", 0)
    redis_command_keys = redis_client.keys("command*")
    redis_command_keys = [k.decode() for k in redis_command_keys]
    for key in redis_command_keys:
        redis_client.delete(key)
    redis_client.set("flag", 0)
    return render_template('index.html')


# 스캔 결과 받아서 공격 필터링
@bp.route('/scan-result', methods=['GET', 'POST'])
def get_scan_result():
    if request.method == 'POST':
        try:
            scan_result = request.get_json() # 에이전트에서 보낸 포트 스캔 결과(json)
            print('scan_result : ', scan_result)
            filtered_attack = set() # 프론트로 보낼 db에 있는 공격들
            if type(scan_result) == dict:
                scan_result = [ scan_result ]

            for result in scan_result:
                #attacks = Attack.query.filter((Attack.program==result["service_product"])|(Attack.port==result["port"])).all()
                try:
                    attacks = Attack.query.filter(Attack.program==result["service_product"]).with_entities(Attack.attackId).all()
                except:
                    continue
                print('attacks : ', attacks)
                if attacks:
                    for attack in attacks:
                        print('attack : ', attack)
                        filtered_attack.add(attack.attackId)
                for attack_id in filtered_attack:
                    redis_client.sadd("attackList", attack_id)
            # redis_client.delete(f"command{src_ip_n}")
            redis_client.set("flag", 1)
            # res = redis_client.smembers("attackList")
            return { "status":200, "result":"redis에 attackList set type으로 저장 완료" }
            # redis에 attackList set type으로 저장 완료
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
<<<<<<< HEAD
    try:   
        '''
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
        '''
        return {
                    "result" : [
                                                {
                                        "attackId":3,
                                        "program":"bandi",
                                        "version":"1.1",
                                        "port":80,
                                        "fileName":"bandi",
                                        "usage":"fuck"
                                    },
                                                    {
                                        "attackId":4,
                                        "program":"alzip",
                                        "version":"2.1",
                                        "port":80,
                                        "fileName":"alzip",
                                        "usage": " i dont know"
                                    },
                    
                                            ]
                }
        
=======
    try:
        type = request.args.get('type') # 'product' or 'endpoint'
        src_ip = request.args.get('src_ip')
        dst_ip = request.args.get('dst_ip')
        filtered_attack = []
        if type=='product': # 보안장비 점검
            attacks = Attack.query.all()
            for attack in attacks:
                filtered_attack.append({
                    "attackId":attack.attackId,
                    "program":attack.program,
                    "version":attack.version,
                    "port":attack.port,
                    "fileName":attack.fileName,
                    "usage":attack.usage
                })
            return {"result":filtered_attack}
            # return jsonify({'data': render_template('index.html', CVE_list=filtered_attack)})
        else: # target 점검
            # src_ip에게 dst_ip를 포트스캔하라 명령 저장
            redis_client.set("flag", 0)
            if redis_client.hget('agent_ip_list', src_ip) == None:
                return "this src_ip is not stored in Redis"
            src_ip_n = int(redis_client.hget('agent_ip_list', src_ip).decode())
            redis_client.hmset(f'command{src_ip_n}', {
                "type":"scan",
                "target_ip":dst_ip
            })

            while int(redis_client.get("flag").decode())==0:
                time.sleep(3)
            # flag가 1로 바뀌어서 반복문에서 벗어남
            # flag 다시 세팅, attack_list가 redis에 저장되어있는 상태
            redis_client.set("flag", 0)
            attackList = redis_client.smembers("attackList")
            print('attackList from redis : ', attackList)
            filtered_attack = []
            for attackId in attackList:
                attack_id = int(attackId.decode())
                attacks = Attack.query.filter(Attack.attackId==attack_id).all()

                for attack in attacks:
                    filtered_attack.append({
                    "attackId":attack.attackId,
                    "program":attack.program,
                    "version":attack.version,
                    "port":attack.port,
                    "fileName":attack.fileName,
                    "usage":attack.usage
                })
            return {"result":filtered_attack}
            # return render_template('index.html', CVE_list=filtered_attack)
            # comm = redis_client.hgetall(f'command{src_ip_n}')
            # comm = { key.decode(): val.decode() for key, val in comm.items() }
            # #print(comm)
            # return comm
            # return redirect(url_for('attack._list'))
>>>>>>> 0ea9ce2f1d047a16f8a81a3afd1385e6a57d88fe
    except Exception as e:
        print('/cve/filter Error : ', e)
        return {
            "status":"600"
        }

# attackStart 버튼 클릭 시 
@bp.route('/attack/start')
def attackStartButtonClicked():
    try:
        attackType = request.args.get('type') # 'product' or 'endpoint'
        src_ip = request.args.get('src_ip')
        dst_ip = request.args.get('dst_ip')
        # 백에서 받은 db에 저장된 attackIdx 그대로 다시 돌려줘야함.
        attackIdx = request.args.get('cve_id')
        
        if redis_client.hget('agent_ip_list', src_ip) == None: # src는 무조건 agent, dst는 agent일 수도 target일 수도
            return "this src_ip or dst_ip is not stored in Redis"
        src_ip_n = int(redis_client.hget('agent_ip_list', src_ip).decode())
        redis_all_keys = redis_client.keys("*")
        redis_all_keys = [ i.decode() for i in redis_all_keys]
        attackInfo = Attack.query.filter(Attack.attackId==attackIdx).first()
        print('attackInfo.port : ', type(attackInfo.port))
        attackName = attackInfo.fileName
        if f"command{src_ip_n}" in redis_all_keys: # 이미 할당된 명령 ex.scan이 있으면 삭제해버리기
            redis_client.delete(f"command{src_ip_n}")

        if attackType == "target": # target 공격
            redis_client.hmset(f'command{src_ip_n}', {
                "type":"attack_target",
                "download": f"http://{MyIP}:5000/download/{attackName}",
                "target_ip": dst_ip,
                "target_port": attackInfo.port,
                "usage": attackInfo.usage
            })
        else: # product 공격
            redis_client.hmset(f'command{src_ip_n}', {
                "type":"attack_secu",
                "download": f"http://{MyIP}:5000/download/{attackName}",
                "target_ip": dst_ip,
                "target_port": attackInfo.port,
                "usage": attackInfo.usage
            })

            dst_ip_n = int(redis_client.hget('agent_ip_list', dst_ip).decode())
            redis_client.hmset(f'command{dst_ip_n}', {
                "type":"defense"
            })
        return {
            "result":200
        }
    except Exception as e:
        print('/attack/start Error : ', e)
        return {
            "result":600
        }


@bp.route('/utilities-other.html')
def utilities():
    return render_template('utilities-other.html')


@bp.route('/command/<int:agentId>')
def commandToAgent(agentId):
    redis_all_keys = redis_client.keys("*")
    redis_all_keys = [ i.decode() for i in redis_all_keys]
    if f"command{agentId}" in redis_all_keys:
        comm = redis_client.hgetall(f'command{agentId}')
        comm = { key.decode(): val.decode() for key, val in comm.items() }
        # print('comm : ', comm)
        redis_client.delete(f"command{agentId}")
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
    print('/download file_name : ', file_name)
    if os.path.isfile(file_name):
        return send_file(file_name,
                        mimetype='text/x-python',
                        attachment_filename=f"{attackName}.py",# 다운받아지는 파일 이름 -> 경로 지정할 수 있나?
                        as_attachment=True)
    else:
        return "wrong attackName"


@bp.route('/report/<int:agentId>', methods=["POST"])
def report(agentId):
    try:
        if request.method == 'POST':
            data = request.get_json()
            pkts = data["pkts"]
            # pkts가 binary로 오던데 어떻게 받을 것인가. 오는 형태를 봐야할 듯.
            attackName = data["attackName"]
            print("agentId : ", agentId)
            print("pkts : ", pkts)
            print("attackName : ", attackName)

            crawled_description = crawler.crawl(attackName)
            if crawled_description == None:
                return "crawling error!"
            else:
                return crawled_description
            # 프론트로 어떻게 리턴할 것인지는 아직
        return
    except Exception as e:
        print('report Error : ',e)
        return


####################################################################################
############## FOR US ##############################################################
@bp.route('/insert/db', methods=['POST'])
def insert_into_db():
    try:
        if request.method=='POST':
            data = request.get_json()
            print(data)
            print(data["program"], data["version"], data["port"], data["fileName"], data["usage"], data["description"])
            attack = Attack(program=data["program"], version=data["version"], port=data["port"], fileName=data["fileName"], usage=data["usage"], description=data["description"])
            db.session.add(attack)
            db.session.commit()
            return {"result":True}
            
    except Exception as e:
        print('insert db Error : ', e)
        return False