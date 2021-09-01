from flask import Blueprint, request, send_file, current_app

from app.models import Attack
# from app import sckt
import os, bson

import json
import logging
import logging.config
import pathlib
log_config = (pathlib.Path(__file__).parent.resolve().parents[1].joinpath("log_config.json"))
config = json.load(open(str(log_config)))
logging.config.dictConfig(config)
logger = logging.getLogger(__name__)

from flask_mail import Mail, Message

from app.modules import parser, sckt_utils, cmd_setter

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
        all_attacks = parser.query_to_json(attacks)

        logger.info(f"[ATTACK] [*] product  /filter - \"result\" : {all_attacks}")
        
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

        logger.info(f"[ATTACK] [*] endpoint  /filter - \"scan_result\" : {recvData}")
        
        sckt.close()
        filtered_attacks = parser.recv_to_json(recvData)
        res = {"result":filtered_attacks}
        
        logger.info(f"[ATTACK] [*] endpoint /filter - \"filtered_attacks\" : {res}")
        
        return {"result":filtered_attacks}


@bp.route('/start')
def attack_start():
    attackType = request.args.get('type') # 'product' or 'endpoint'
    src_ip = request.args.get('src_ip')
    try:
        dst_ip = request.args.get('dst_ip')
    except:
        pass
    # attack_id_list = request.args.get("cve_id") # [attackId 리스트]
    attack_id_list = [request.args.get("cve_id")]

    command = {"type":"web"}

    if attackType=="product": # (attack & defense) & remote malware
        _command = cmd_setter.product_command(src_ip, dst_ip, attack_id_list)
    elif attackType=="endpoint": # target
        _command = cmd_setter.target_command(src_ip, dst_ip, attack_id_list)
    elif attackType=="local_malware": # local malware
        _command = cmd_setter.malware_command(src_ip, attack_id_list)
    
    command["command"]=_command

    logger.info(f"[ATTACK] /start - attackInfo : {attackType}, {src_ip}, {dst_ip}, {attack_id_list}")
    logger.info(f"[ATTACK] /start - command : {command}")

    sckt = sckt_utils.create_socket()
    sckt.send(bson.dumps(command))
    sckt.close()
    return "OK"


# 암호화 된
@bp.route('/download/crypt/<int:attackIdx>/', methods=['GET'])
def attack_download_enc(attackIdx):
    attackInfo = Attack.query.filter(Attack.attackId==attackIdx).first()
    f_name = attackInfo.fileName

    pwd = os.getcwd()
    file_route = f"{pwd}/attack_files/{f_name}" # 공격 파일 경로

    logger.info(f"[ATTACK] /download/crypt/{attackIdx} - File Route : {file_route}")
    
    file_bytes = bytearray(open(file_route, 'rb').read())
    f_size = cmd_setter.file_size(file_route)
    encoded = bytearray(f_size)

    for i in range(f_size):
        encoded[i] = file_bytes[i]^ord('X')
    
    logger.info(f"[ATTACK] /download/crypt/{attackIdx} - Encoded File : {encoded}")

    return encoded



# 암호화 안 된
@bp.route('/download/<int:attackIdx>/', methods=['GET'])
def attack_download(attackIdx):
    attackInfo = Attack.query.filter(Attack.attackId==attackIdx).first()
    file_name = attackInfo.fileName

    pwd = os.getcwd()
    file_name = f"{pwd}/attack_files/{file_name}" # 공격 파일 경로

    logger.info(f"[ATTACK] /download/{attackIdx} - File Name : {file_name}")

    if os.path.isfile(file_name):
        return send_file(file_name,
            attachment_filename=f"{file_name}",# 다운받아지는 파일 이름 -> 경로 지정할 수 있나?
            as_attachment=True)
    else:
        return "wrong file_name"


@bp.route('/mail', methods=['POST'])
def attack_mail():
    if request.method=='GET':
        logger.warning("[ATTACK] /mail - NOT GET Method")
        return
    
    sender_email = email_info.email
    sender_pw = email_info.passwd

    logger.info(f"[ATTACK] /mail - sender_email :{sender_email}, sender_pw :{sender_pw}")
    # logger.info(f"[ATTACK] /mail - request.form : {request.form}")
    # logger.info(f"[ATTACK] /mail - request.files : {request.files}")
    
    recver_email = request.form.getlist('recver_email')[0]
    file_title = request.form.getlist('title')[0]
    file_body = request.form.getlist('body')[0]
    file_name = request.files.getlist('attachment')[0]
    fileName = file_name.filename
    
    logger.info(f"[ATTACK] /mail - recver_email : {recver_email}, file_title : {file_title}, file_body : {file_body}, fileName : {fileName}")
    

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
    return "OK"



    