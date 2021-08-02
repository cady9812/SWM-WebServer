from app.models import Attack
from app import MyIP
import os


downloadURL = f"http://{MyIP}:5000/attack/download"


def file_size(file_route):
    # pwd = os.getcwd()
    # file_name = f"{pwd}\\attack_files\\{file_name}" # 공격 파일 경로
    # f_size = os.path.getsize(file_name)
    return os.path.getsize(file_route)



def product_command(src_ip, dst_ip, attack_id_list):
    pwd = os.getcwd()
    
    command = []
    for attack_id in attack_id_list:
        file_name, dst_port, usage, type = Attack.query.filter(Attack.attackId==attack_id).with_entities(Attack.fileName, Attack.port, Attack.usage, Attack.type).first()
        if type=="malware":
            chk = True
        else:
            chk = False
        # file_route = f"{downloadURL}/crypt/{attack_id}"
        file_route = f"{pwd}/attack_files/{file_name}"
        down_route = f"{downloadURL}/crypt/{attack_id}"
        command.append({
            "type":"defense",
            "src_ip": dst_ip,
            "attack_id":attack_id,
            "port":dst_port
        })
        command.append({
            "type":"attack_secu",
            "malware":chk,
            "src_ip":src_ip,
            "dst_ip":dst_ip,
            "dst_port":dst_port,
            "download":down_route, # 암호화 된
            "file_size":file_size(file_route), # bytes
            "attack_id":attack_id,
            "usage":usage
        })
    return command




def target_command(src_ip, dst_ip, attack_id_list):
    command = []
    pwd = os.getcwd()
    for attack_id in attack_id_list:
        file_name, dst_port, usage = Attack.query.filter(Attack.attackId==attack_id).with_entities(Attack.fileName, Attack.port, Attack.usage).first()
        # file_route = f"{downloadURL}/{attack_id}"
        file_route = f"{pwd}/attack_files/{file_name}"
        down_route = f"{downloadURL}/crypt/{attack_id}"
        command.append({
            "type":"attack_target",
            "src_ip":src_ip,
            "dst_ip":dst_ip,
            "dst_port":dst_port,
            "download":down_route, # 암호화 안 된
            "file_size":file_size(file_route), # bytes,
            "attack_id":attack_id,
            "usage":usage
        })
    return command



def malware_command(src_ip, attack_id_list):
    command = []
    pwd = os.getcwd()
    for attack_id in attack_id_list:
        file_name, usage = Attack.query.filter(Attack.attackId==attack_id).with_entities(Attack.fileName, Attack.port, Attack.usage).first()
        file_route = f"{pwd}/attack_files/{file_name}"
        down_route = f"{downloadURL}/{attack_id}"
        command.append({
            "type":"malware",
            "src_ip":src_ip,
            "download":down_route, # 암호화 안 된
            "file_size":file_size(file_route),
            "attack_id":attack_id,
            "usage":usage
        })
    return command
         

