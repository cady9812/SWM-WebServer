from flask import Blueprint, request

import base64

import json
import logging
import logging.config
import pathlib
log_config = (pathlib.Path(__file__).parent.resolve().parents[1].joinpath("log_config.json"))
config = json.load(open(str(log_config)))
logging.config.dictConfig(config)
logger = logging.getLogger(__name__)



bp = Blueprint('report', __name__, url_prefix='/report')


@bp.route('/pkt', methods=['POST'])
def report_pkt():
    if request.method=='GET':
        logger.warning("[REPORT] /pkt - NOT GET Method")
        return
    # 일단 받아놓기만 하기
    data = request.get_json()
    attack_id = data["attack_id"]
    port = data["port"]
    send_ip = data["send_ip"]
    recv_ip = data["recv_ip"]
    send_pkt = data["send"]
    recv_pkt = data["recv"]
    logger.info("[REPORT] Packet Recv")
    logger.info(f"attack_ip : {attack_id} / port : {port} / send_ip : {send_ip} \
/ recv_ip : {recv_ip} / send_pkt : {send_pkt} / recv_pkt :{recv_pkt}")
    for s in send_pkt:
        print('[decoded] s : ', base64.b64decode(s))
    for r in recv_pkt:
        print('[decoded] r : ', base64.b64decode(r))
    return

@bp.route('/target', methods=['POST'])
def report_target():
    if request.method=='POST':
        logger.warning("[REPORT] /target - NOT GET Method")
        return
    data = request.get_json()
    attack_id = data["attack_id"]
    pkt = data["pkt"]
    logger.info("[REPORT] Target Recv")
    return