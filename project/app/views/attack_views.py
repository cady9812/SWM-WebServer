from flask import Blueprint, request, send_file
from app.models import Attack
from app import sckt
import os, bson

import json
import logging
import logging.config
import pathlib
log_config = (pathlib.Path(__file__).parent.resolve().parents[1].joinpath("log_config.json"))
config = json.load(open(str(log_config)))
logging.config.dictConfig(config)
logger = logging.getLogger(__name__)


from app.modules import parser, sckt_recv, setter

bp = Blueprint('attack', __name__, url_prefix='/attack')


# nextCVE 버튼 클릭
# /cve/fileter  nextCVEButtonClicked()
@bp.route('/filter')
def attack_filter():
    global sckt
    type = request.args.get('type') # 'product' or 'endpoint'
    src_ip = request.args.get('src_ip')
    dst_ip = request.args.get('dst_ip')
    if type=='product':
        attacks = Attack.query.all()
        all_attacks = parser.query_to_json(attacks)
        return {"result":all_attacks}
    elif type=='endpoint':
        command = {
            "type":"web",
            "command":[{
                "type":"scan",
                "src_ip":src_ip,
                "dst_ip":dst_ip
            }]
        }
        sckt.send(bson.dumps(command))
        sckt, recvData = sckt_recv.recv_data(sckt)
        filtered_attacks = parser.recv_to_json(recvData)
        return {"result":filtered_attacks}


# attackStart 버튼 클릭 시 
# /attack/start  attackStartButtonClicked()
@bp.route('/start')
def attack_start():
    attackType = request.args.get('type') # 'product' or 'endpoint'
    src_ip = request.args.get('src_ip')
    try:
        dst_ip = request.args.get('dst_ip')
    except:
        pass
    attack_id_list = request.get_json()["cve_id"] # [attackId 리스트]
    command = []
    if attackType=="product": # (attack & defense) & remote malware
        command = setter.product_command(src_ip, dst_ip, attack_id_list)
        sckt.send(bson.dumps(command))
    elif attackType=="endpoint": # target
        command = setter.target_command(src_ip, dst_ip, attack_id_list)
        sckt.send(bson.dumps(command))
    elif attackType=="local_malware": # local malware
        command = setter.malware_command(src_ip, attack_id_list)
        sckt.send(bson.dumps(command))
    return

# 공격 코드 다운받는 링크
# 암호화 된
@bp.route('/download/crypt/<int:attackIdx>/', methods=['GET'])
def attack_download_enc(attackIdx):
    attackInfo = Attack.query.filter(Attack.attackId==attackIdx).first()
    file_name = attackInfo.fileName

    pwd = os.getcwd()
    file_route = f"{pwd}\\attack_files\\{file_name}" # 공격 파일 경로
    logger.info(f"[ATTACK] File Route : {file_route}")
    
    file_bytes = bytearray(open(file_route, 'rb').read())
    f_size = setter.file_size(file_route)
    encoded = bytearray(f_size)

    for i in range(f_size):
        encoded[i] = file_bytes[i]^ord('X')
    logger.info(f"[ATTACK] Encoded File : {encoded}")

    return {"encrypted":encoded}


# 공격 코드 다운받는 링크
# 암호화 안 된
@bp.route('/download/<int:attackIdx>/', methods=['GET'])
def attack_download(attackIdx):
    attackInfo = Attack.query.filter(Attack.attackId==attackIdx).first()
    file_name = attackInfo.fileName

    pwd = os.getcwd()
    file_name = f"{pwd}\\attack_files\\{file_name}" # 공격 파일 경로
    if os.path.isfile(file_name):
        return send_file(file_name,
            attachment_filename=f"{file_name}",# 다운받아지는 파일 이름 -> 경로 지정할 수 있나?
            as_attachment=True)
    else:
        return "wrong file_name"