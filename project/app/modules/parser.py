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

