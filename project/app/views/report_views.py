from flask import Blueprint, request

import base64

# import json
# import logging
# import logging.config
# import pathlib
# log_config = (pathlib.Path(__file__).parent.resolve().parents[1].joinpath("log_config.json"))
# config = json.load(open(str(log_config)))
# logging.config.dictConfig(config)
# logger = logging.getLogger(__name__)

from app.models import Report
from app.modules import json_parser, loggers, statusCode
from app import db

logger = loggers.create_logger(__name__)



bp = Blueprint('report', __name__, url_prefix='/report')


@bp.route('/')
def get_all_reports():
    reports = Report.query.with_entities(Report.no, Report.startTime).distinct().order_by(Report.no.desc())
    arranged_reports = json_parser.report_query_to_json(reports)
    return {
        "status": statusCode.OK
    }

@bp.route('/<int:reportNo>')
def show_one_report(reportNo):
    reports = Report.query.filter(Report.no==reportNo).all()
    arranged_reports = []
    for report in reports:
        arranged_reports.append({
            "no":report.no,
            "attack_id":report.attackId,
            "time":report.startTime,
            "log":report.log
        })
    return {
        "status":statusCode.SERVER_ERROR
    }


# @bp.route('/pkt', methods=['POST'])
# def report_pkt():
#     if request.method=='GET':
#         logger.warning("\n[REPORT] /pkt - NOT GET Method")
#         return
#     # 일단 받아놓기만 하기
#     data = request.get_json()
#     attack_id = data["attack_id"]
#     port = data["port"]
#     send_ip = data["send_ip"]
#     recv_ip = data["recv_ip"]
#     send_pkt = data["send"]
#     recv_pkt = data["recv"]

#     logger.info(f"\n[REPORT] /pkt - attack_ip : {attack_id} / port : {port} / send_ip : {send_ip} \
# / recv_ip : {recv_ip} / send_pkt : {send_pkt} / recv_pkt :{recv_pkt}")

#     # [REPORT] /pkt - 
#     # attack_ip : 7 / port : 0 / send_ip : 192.168.0.208 / recv_ip : 192.168.0.158 / 
#     # send_pkt : ['UE9TVCAvd3AtYWRtaW4vcG9zdC5waHAgSFRUUC8xLjENCkhvc3Q6IDEyNy4wLjAuMTo0MDY3OQ0KVXNlci1BZ2VudDogcHl0aG9uLXJlcXVlc3RzLzIuMjIuMA0KQWNjZXB0LUVuY29kaW5nOiBnemlwLCBkZWZsYXRlDQpBY2NlcHQ6ICovKg0KQ29ubmVjdGlvbjoga2VlcC1hbGl2ZQ0KQ29udGVudC1MZW5ndGg6IDE1OA0KQ29udGVudC1UeXBlOiBhcHBsaWNhdGlvbi94LXd3dy1mb3JtLXVybGVuY29kZWQNCg0K', 'X3dwbm9uY2U9ZHJlYW1oYWNrJmFjdGlvbj1lZGl0cG9zdCZwb3N0X0lEPWRyZWFtaGFjayZtZXRhX2lucHV0JTVCX3dwX2F0dGFjaGVkX2ZpbGUlNUQ9MjAyMSUyRjA5ZHJlYW1oYWNrJTNGJTJGLi4lMkYuLiUyRi4uJTJGLi4lMkZ0aGVtZXMlMkZkcmVhbWhhY2slMkZyYWhhbGk=']

#     for s in send_pkt:
#         logger.info(f'\n[decoded] s : {base64.b64decode(s)}')
#         # b'POST /wp-admin/post.php HTTP/1.1\r\nHost: 127.0.0.1:40679\r\nUser-Agent: python-requests/2.22.0\r\nAccept-Encoding: gzip, deflate\r\nAccept: */*\r\nConnection: keep-alive\r\nContent-Length: 158\r\nContent-Type: application/x-www-form-urlencoded\r\n\r\n'
#         # b'_wpnonce=dreamhack&action=editpost&post_ID=dreamhack&meta_input%5B_wp_attached_file%5D=2021%2F09dreamhack%3F%2F..%2F..%2F..%2F..%2Fthemes%2Fdreamhack%2Frahali'
        
#     for r in recv_pkt:
#         logger.info(f'\n[decoded] r : {base64.b64decode(r)}')
#     return "OK"


# @bp.route('/malware', methods=['POST'])
# def report_target():
#     if request.method=='GET':
#         logger.warning("\n[REPORT] /target - NOT GET Method")
#         return
#     data = request.get_json()
#     attack_id = data["attack_id"]
#     infected = data["infected"]
#     logger.info(f"\n[REPORT] /target - attack_id : {attack_id}, infected : {infected}")
#     return

# @bp.route('/kvm', methods=['POST'])
# def report_kvm():
#     if request.method=='GET':
#         logger.warning("\n[REPORT] /kvm - NOT GET Method")
#         return
#     data = request.get_json()
#     attack_id = data["attack_id"]
#     log = data["log"]