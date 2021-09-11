from flask import Blueprint, request, send_file, current_app

from app.models import Attack, Report

import os, bson, json
import time
import datetime

from app.modules import loggers, statusCode, json_parser, sckt_utils, cmd_setter
logger = loggers.create_logger(__name__)


from flask_mail import Mail, Message
from private import email_info


bp = Blueprint('attack', __name__, url_prefix='/attack')


@bp.route('/filter')
def attack_filter():
    # global sckt
    type = request.args.get('type') # 'product' or 'endpoint'
    src_ip = request.args.get('src_ip')
    dst_ip = request.args.get('dst_ip')
    if type=='product':
        attacks = Attack.query.all()
        all_attacks = json_parser.attack_query_to_json(attacks)

        logger.info(f"\n[ATTACK] [*] product  /filter - \"result\" : {all_attacks}")
        
        return {"result":all_attacks}
    elif type=='endpoint':
        sckt = sckt_utils.create_socket()
        command = {
            "type":"web",
            "command":[{
                "type":"scan",
                "src_ip":src_ip,
                "dst_ip":dst_ip
            }]
        }
        sckt.send(bson.dumps(command))
        recvData = sckt_utils.recv_data(sckt)

        logger.info(f"\n[ATTACK] [*] endpoint /filter - \"scan_result\" : {recvData}")
        
        sckt.close()
        filtered_attacks = json_parser.recv_to_json(recvData)
        res = {"result":filtered_attacks}
        
        logger.info(f"\n[ATTACK] [*] endpoint /filter - \"filtered_attacks\" : {res}")
        
        return {"result":filtered_attacks}
    elif type=="malware":
        attacks = Attack.query.filter(Attack.type=="mal").all()
        all_attacks = json_parser.attack_query_to_json(attacks)

        logger.info(f"\n[ATTACK] [*] malware  /filter - \"result\" : {all_attacks}")
        
        return {"result":all_attacks}



@bp.route('/start', methods=['POST'])
def attack_start():
    getFromFront = request.get_data().decode()
    getFromFront = json.loads(getFromFront)

    logger.info(f"\n[ATTACK] /start - getFromFront : {getFromFront}")

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

    logger.info(f"\n[ATTACK] /start - attackInfo : {attackType}, {src_ip}, {dst_ip}, {attack_id_list}")
    logger.info(f"\n[ATTACK] /start - command : {command}")

    sckt = sckt_utils.create_socket()
    sckt.send(bson.dumps(command)) # send command to tcp server
    
    try:
        pre_no = Report.query.order_by(Report.no.desc()).first().no
    except:
        pre_no = -1
    now = datetime.datetime.now()
    attack_start_time = now.strftime('%Y-%m-%d %H:%M:%S')

    for i in range(attack_cnt): # recv reports from tcp server
        reportData = sckt_utils.recv_data(sckt) # json
        to_MySQL_result = json_parser.save_report_to_MySQL(pre_no, attack_start_time, reportData)
        if to_MySQL_result == "Insert ERROR":
            logger.warning("\n[ATTACK] /start - ERROR while Insert Report into MySQL")
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

    logger.info(f"\n[ATTACK] /download/crypt/{attackIdx} - File Route : {file_route}")
    
    file_bytes = bytearray(open(file_route, 'rb').read())
    f_size = cmd_setter.file_size(file_route)
    encoded = bytearray(f_size)

    for i in range(f_size):
        encoded[i] = file_bytes[i]^ord('X')
    
    logger.info(f"\n[ATTACK] /download/crypt/{attackIdx} - Encoded File : {encoded}")

    return encoded



# 암호화 안 된
@bp.route('/download/<int:attackIdx>/', methods=['GET'])
def attack_download(attackIdx):
    attackInfo = Attack.query.filter(Attack.attackId==attackIdx).first()
    file_name = attackInfo.fileName

    pwd = os.getcwd()
    file_name = f"{pwd}/attack_files/{file_name}" # 공격 파일 경로

    logger.info(f"\n[ATTACK] /download/{attackIdx} - File Name : {file_name}")

    if os.path.isfile(file_name):
        return send_file(file_name,
            attachment_filename=f"{file_name}",# 다운받아지는 파일 이름 -> 경로 지정할 수 있나?
            as_attachment=True)
    else:
        return {"status":statusCode.SERVER_ERROR}


@bp.route('/mail', methods=['POST'])
def attack_mail():
    if request.method=='GET':
        logger.warning("\n[ATTACK] /mail - NOT GET Method")
        return {"status":statusCode.METHOD_ERROR}
    
    sender_email = email_info.email
    sender_pw = email_info.passwd

    logger.info(f"\n[ATTACK] /mail - sender_email :{sender_email}, sender_pw :{sender_pw}")
    # logger.info(f"[ATTACK] /mail - request.form : {request.form}")
    # logger.info(f"[ATTACK] /mail - request.files : {request.files}")
    
    recver_email = request.form.getlist('recver_email')[0]
    file_title = request.form.getlist('title')[0]
    file_body = request.form.getlist('body')[0]
    file_name = request.files.getlist('attachment')[0]
    fileName = file_name.filename
    
    logger.info(f"\n[ATTACK] /mail - recver_email : {recver_email}, file_title : {file_title}, file_body : {file_body}, fileName : {fileName}")
    

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



    