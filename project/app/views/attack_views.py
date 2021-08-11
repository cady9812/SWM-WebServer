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
        print("!", recvData)  #TODO
        sckt.close()
        filtered_attacks = parser.recv_to_json(recvData)
        res = {"result":filtered_attacks}
        print('[!!] res : ', res)
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

    logger.info(f"[ATTACK] /start - attackInfo : {attackType}, {src_ip}, {dst_ip}, {attack_id_list}")

    command = {"type":"web"}

    if attackType=="product": # (attack & defense) & remote malware
        _command = cmd_setter.product_command(src_ip, dst_ip, attack_id_list)
    elif attackType=="endpoint": # target
        _command = cmd_setter.target_command(src_ip, dst_ip, attack_id_list)
    elif attackType=="local_malware": # local malware
        _command = cmd_setter.malware_command(src_ip, attack_id_list)
    
    command["command"]=_command

    logger.info(f"[ATTACK] /start - command : {command}")

    sckt = sckt_utils.create_socket()
    sckt.send(bson.dumps(command))
    sckt.close()
    return


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
    sender_email = request.form['sender_email']
    sender_pw = request.form['sender_pw']
    recver_email = request.form['recver_email']
    file = request.files['FILE_TAG']
    fileName = file.filename

    smtp_type = sender_email.split('@')[1]

    logger.info(f"[ATTACK] /mail - sender_email:{sender_email}, sender_pw:{sender_pw}, recver_email:{recver_email}, fileName:{fileName}, smtp_type:{smtp_type}")

    # sender_email 파싱해서 수정 필요
    current_app.config['MAIL_SERVER']=f"smtp.{smtp_type}" # smtp.naver.com / smtp.gmail.com / smtp.daum.net
    current_app.config['MAIL_PORT']=465
    current_app.config['MAIL_USERNAME']=sender_email
    current_app.config['MAIL_PASSWORD']=sender_pw
    current_app.config['MAIL_USE_TLS']=False
    current_app.config['MAIL_USE_SSL']=True

    mail = Mail(current_app)

    msg = Message('Hello', sender=sender_email, recipients=[recver_email])

    with current_app.open_resource(f"../attack_files/{fileName}") as fp:
        msg.attach(f"{fileName}", "text/x-python", fp.read())

    # msg.body = "hello I'm from flask"
    mail.send(msg)
    return



    