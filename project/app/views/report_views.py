from flask import Blueprint, request

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
    send_ip = data["send_ip"]
    recv_ip = data["recv_ip"]
    send_pkt = data["send"]
    recv_pkt = data["recv"]
    logger.info("[REPORT] Packet Recv")
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