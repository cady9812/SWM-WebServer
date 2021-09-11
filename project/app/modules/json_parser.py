from app.models import Attack, Report
from app import MyIP, db

from app.modules import loggers
logger = loggers.create_logger(__name__)

from private.ports import WEB_SERVER_PORT
downloadURL = f"https://{MyIP}:{WEB_SERVER_PORT}/attack/download/"


def attack_query_to_json(attacks):
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


# for report main page
def report_query_to_json(reports):
    arranged_reports = []
    for report in reports:
        report_no = report[0]
        report_startTime = report[1]
        attackId_db = Report.query.with_entities(Report.attackId).filter(Report.no==report_no)
        attackId_list = [int(i[0]) for i in attackId_db]
        _report = {
            "no":report_no,
            "attack_id":attackId_list,
            "start_time":report_startTime
        }
        arranged_reports.append(_report)
    return arranged_reports


def recv_to_json(recvData):
    filtered_attacks = []
    ports = recvData["ports"]
    for _port in ports:
        try:
            attacks = Attack.query.filter(Attack.program==_port["service_name"]).all()
        except:
            continue
        sub_filtered_attacks= attack_query_to_json(attacks)
        filtered_attacks.extend(sub_filtered_attacks)
    return filtered_attacks



def save_report_to_MySQL(pre_no, attack_start_time, reportData):
    new_no = pre_no+1
    reportType = reportData["type"]
    attack_id = reportData["attack_id"] # int
    if reportType=="pkt":
        port = reportData["port"] # int
        send_ip = reportData["send_ip"]
        recv_ip = reportData["recv_ip"]
        sendPkts = reportData["send"] # list
        str_sendPkts = str(sendPkts) # str
        recvPkts = reportData["recv"] # list
        str_recvPkts = str(recvPkts) # str
        log = f"{send_ip} sent {str_sendPkts} \n {recv_ip} received {str_recvPkts}"
    elif reportType=="malware":
        attackName = Attack.query.filter(Attack.attackId==attack_id).first().fileName
        infected = reportData["infected"] # bool
        if infected==True:
            log = f"Infected by {attackName}"
        else:
            log = f"Not Infected by {attackName}"
    elif reportType=="kvm":
        log = reportData["log"]
    try:
        print(f"New Report : {new_no}, {attack_id}, {log}, {attack_start_time}")
        
        # Insert into MySQL
        report = Report(no=new_no, attackId=attack_id, startTime=attack_start_time, log=log)
        db.session.add(report)
        db.session.commit()
        return "Insert SUCCESS"
    except:
        return "Insert ERROR"
