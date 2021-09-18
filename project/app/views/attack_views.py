from flask import Blueprint, request, send_file, current_app
from app.models import Attack, Report
from flask_mail import Mail, Message
from private import email_info

import os, bson, json
import time
import datetime

from app.modules import loggers, statusCode, parser, sckt_utils, cmd_setter
logger = loggers.create_logger(__name__)


bp = Blueprint('attack', __name__, url_prefix='/attack')


@bp.route('/filter')
def attack_filter():
    type1 = request.args.get('type1') # product, endpoint, malware
    src_ip = request.args.get('src_ip')
    dst_ip = request.args.get('dst_ip')
    
    if type1=='product':### 보안 장비 점검
        type2 = request.args.get('type2') # atk_packet, atk+malware
        type2 = "mal" if type2=="atk_malware" else "cve"
        attacks = Attack.query.filter(Attack.type==type2).all()
        all_attacks = parser.attack_query_to_json(attacks)
        logger.info(f"[ATTACK] PRODUCT : {all_attacks}")
        return {"result":all_attacks}

    elif type1=='endpoint':### 타겟 점검
        sckt = sckt_utils.create_socket()
        command = {
            "type":"web",
            "command":[{
                "type":"scan",
                "src_ip":src_ip,
                "dst_ip":dst_ip
            }]
        }
        sckt_utils.send_with_size(sckt, bson.dumps(command))
        recvData = sckt_utils.recv_data(sckt)
        logger.info(f"[ATTACK] ENDPOINT \"scan_result\" : {recvData}")
        sckt.close()

        # filter by middle category in MySQL
        filtered_attacks = parser.recv_to_json(recvData)
        # res = {"result":filtered_attacks}
        # logger.info(f"[ATTACK] ENDPOINT \"filtered_attacks\" : {res}")
        return {"result":filtered_attacks}

    elif type1=="malware":### endpoint 솔루션
        attacks = Attack.query.filter(Attack.type=="mal").all()
        all_attacks = parser.attack_query_to_json(attacks)

        logger.info(f"[ATTACK] MALWARE \"result\" : {all_attacks}")
        
        return {"result":all_attacks}



@bp.route('/start', methods=['POST'])
def attack_start():
    getFromFront = request.get_data().decode()
    getFromFront = json.loads(getFromFront)

    logger.info(f"[ATTACK] data from front : {getFromFront}")

    attackType = getFromFront['type'] # 'product' or 'endpoint'
    src_ip = getFromFront['src_ip']
    try:
        dst_ip = getFromFront['dst_ip']
    except:
        pass
    attack_id_list = getFromFront["cve_id"]
    attack_cnt = len(attack_id_list)

    command = {"type":"web"}

    if attackType=="product": # (attack & defense) & remote malware
        _command = cmd_setter.product_command(src_ip, dst_ip, attack_id_list)
    elif attackType=="endpoint": # target
        _command = cmd_setter.target_command(src_ip, dst_ip, attack_id_list)
    elif attackType=="malware": # local malware
        _command = cmd_setter.malware_command(dst_ip, attack_id_list)
    
    command["command"]=_command

    logger.info(f"[ATTACK] attack info : {attackType}, {src_ip}, {dst_ip}, {attack_id_list}")
    logger.info(f"[ATTACK] command : {command}")

    sckt = sckt_utils.create_socket()
    # send command to tcp server
    sckt_utils.send_with_size(sckt, bson.dumps(command))
    
    try:
        pre_no = Report.query.order_by(Report.no.desc()).first().no
    except:
        pre_no = -1
    now = datetime.datetime.now()
    attack_start_time = now.strftime('%Y-%m-%d %H:%M:%S')

    for i in range(attack_cnt): # recv reports from tcp server
        reportData = sckt_utils.recv_data(sckt) # json
        to_MySQL_result = parser.save_report_to_MySQL(pre_no, attack_start_time, reportData)
        if to_MySQL_result == "Insert ERROR":
            logger.warning(f"{loggers.RED}[ATTACK] ERROR while inserting report into MySQL{loggers.END}")
        time.sleep(1)
    sckt.close()

    ### popup alert

    return {
        "status": statusCode.OK
    }



# 암호화 된
@bp.route('/download/crypt/<int:attackIdx>/', methods=['GET'])
def attack_download_enc(attackIdx):
    attackInfo = Attack.query.filter(Attack.attackId==attackIdx).first()
    f_name = attackInfo.fileName

    pwd = os.getcwd()
    file_route = f"{pwd}/attack_files/{f_name}" # 공격 파일 경로

    logger.info(f"[ATTACK] local file route : {file_route}")
    
    file_bytes = bytearray(open(file_route, 'rb').read())
    f_size = cmd_setter.file_size(file_route)
    encoded = bytearray(f_size)

    for i in range(f_size):
        encoded[i] = file_bytes[i]^ord('X')
    
    logger.info(f"[ATTACK] encoded content of encrypted file({attackIdx}) : {encoded}")

    return encoded



# 암호화 안 된
@bp.route('/download/<int:attackIdx>/', methods=['GET'])
def attack_download(attackIdx):
    attackInfo = Attack.query.filter(Attack.attackId==attackIdx).first()
    file_name = attackInfo.fileName

    pwd = os.getcwd()
    file_route = f"{pwd}/attack_files/{file_name}" # 공격 파일 경로

    logger.info(f"[ATTACK] local file route : {file_route}")

    if os.path.isfile(file_route):
        return send_file(file_route,
            attachment_filename=f"{file_route}",# 다운받아지는 파일 이름 -> 경로 지정할 수 있나?
            as_attachment=True)
    else:
        return {"status":statusCode.SERVER_ERROR}


@bp.route('/mail', methods=['POST'])
def attack_mail():
    if request.method=='GET':
        logger.warning(f"{loggers.RED}[ATTACK] NOT GET{loggers.END}")
        return {"status":statusCode.METHOD_ERROR}
    
    sender_email = email_info.email
    sender_pw = email_info.passwd

    logger.info(f"[ATTACK] sender_email :{sender_email}, sender_pw :{sender_pw}")
    # logger.info(f"[ATTACK] /mail - request.form : {request.form}")
    # logger.info(f"[ATTACK] /mail - request.files : {request.files}")
    
    recver_email = request.form.getlist('recver_email')[0]
    file_title = request.form.getlist('title')[0]
    file_body = request.form.getlist('body')[0]
    file_name = request.files.getlist('attachment')[0]
    fileName = file_name.filename
    
    logger.info(f"[ATTACK] recver_email : {recver_email}, file_title : {file_title}, file_body : {file_body}, fileName : {fileName}")
    

    # hard coding OK...
    smtp_type = sender_email.split('@')[1]

    current_app.config['MAIL_SERVER']=f"smtp.{smtp_type}" # smtp.naver.com / smtp.gmail.com / smtp.daum.net
    current_app.config['MAIL_PORT']=465
    current_app.config['MAIL_USERNAME']=sender_email
    current_app.config['MAIL_PASSWORD']=sender_pw
    current_app.config['MAIL_USE_TLS']=False
    current_app.config['MAIL_USE_SSL']=True

    mail = Mail(current_app)
    msg = Message(subject=file_title, sender=sender_email, recipients=[recver_email])
    msg.body = f"{file_body}"
    with current_app.open_resource(f"../attack_files/{fileName}") as fp:
        msg.attach(f"{fileName}", "text/plain", fp.read())
    mail.send(msg)
    return {"status":statusCode.OK}



    
