from app.models import Attack
from app import MyIP

downloadURL = f"http://{MyIP}:9000/attack/download/"

def query_to_json(attacks):
    filtered_attacks=[]
    for attack in attacks:
        _attack = {
            "attackId":attack.attackId,
            "program":attack.program,
            "version":attack.version,
            "port":attack.port,
            "fileName":attack.fileName,
            "usage":attack.usage
        }
        filtered_attacks.append(_attack)
    return filtered_attacks

def recv_to_json(recvData):
    filtered_attacks = []
    ports = recvData["ports"]
    for _port in ports:
        try:
            attacks = Attack.query.filter(Attack.program==_port["service_product"]).all()
        except:
            continue
        sub_filtered_attacks= query_to_json(attacks)
        filtered_attacks.extend(sub_filtered_attacks)
    return filtered_attacks



# def set_remote_command(src_ip, dst_ip, mal, attack_id_list):
#     command = []
#     for attack_id in attack_id_list:
#         dst_port, usage = Attack.query.filter(Attack.attackId==attack_id).with_entities(Attack.port, Attack.usage).first()
#         command.append({
#             "type":"defense",
#             "src_ip": src_ip,
#             "attack_id":attack_id
#         })
#         command.append({
#             "type":"attack_secu",
#             "malware":mal,
#             "src_ip":src_ip,
#             "dst_ip":dst_ip,
#             "dst_port":dst_port,
#             "download":downloadURL+attack_id,
#             "usage":usage,
#             "attack_id":attack_id
#         })
#     return command

# def set_target_command(src_ip, dst_ip, attack_id_list):
#     command = []
#     for attack_id in attack_id_list:
#         dst_port, usage = Attack.query.filter(Attack.attackId==attack_id).with_entities(Attack.port, Attack.usage).first()
#         command.append({
#             "type":"attack_target",
#             "src_ip":src_ip,
#             "dst_ip":dst_ip,
#             "dst_port":dst_port,
#             "download":downloadURL+attack_id,
#             "usage":usage
#         })
#     return command
