from flask import Blueprint, request
from flask.templating import render_template
from app.models import Attack
from app import redis_client, db
import os


### local logger
# import json
# import logging
# import logging.config
# import pathlib
# log_config = (pathlib.Path(__file__).parent.resolve().parents[1].joinpath("log_config.json"))
# config = json.load(open(str(log_config)))
# logging.config.dictConfig(config)
# logger = logging.getLogger(__name__)


### logstash logger
from app.modules import loggers
logger = loggers.create_logger(__name__)


BUFSIZE = 0x1000

bp = Blueprint('main', __name__, url_prefix='/')


# 메인페이지
@bp.route('/')
def index():
    # redis_client.flushdb()
    # redis_client.set("n", 0)
    # redis_command_keys = redis_client.keys("command*")
    # redis_command_keys = [k.decode() for k in redis_command_keys]
    # for key in redis_command_keys:
    #     redis_client.delete(key)
    # redis_client.set("flag", 0)
    # return render_template('index.html')
    logger.info("\n[MAIN] / - Index Page")
    return render_template('index.html')

# Show MITRE ATT&CK matrix
@bp.route('/upload')
def matrix():
    # logger.info("[MAIN] /upload - page access") # for test
    return render_template('./upload-code.html')

# Upload  Customed Attack file from User
@bp.route('/upload/file',methods=['POST'])
def upload():
    if request.method == 'GET':
        logger.warning("\n[MAIN] /upload/code - NOT GET Method")
        return
    
    file = request.files['FILE_TAG']
    fileName = file.filename
    targetName = request.form['targetName']
    targetVersion = request.form['targetVersion']
    targetPort = request.form['targetPort']
    targetUsage = request.form['targetUsage']
    targetSummary = request.form['targetSummary']
    # attackType = request.form["attackType"]
    # temporary hard coding
    attackType = "cve" # or mal

    logger.info(f"\n[MAIN] /upload/code\nfileName : {fileName}\ntargetName : {targetName}\ntargetVersion : {targetVersion}\ntargetPort : {targetPort}\ntargetUsage : {targetUsage}\ntargetSummary : {targetSummary}\nattackType : {attackType}")

    if Attack.query.filter(Attack.fileName==fileName).first()==None:
        file.save(os.path.join(os.getcwd(), "attack_files", f"{fileName}"))
        
        attack = Attack(fileName=fileName, program=targetName, version=targetVersion, port=targetPort, usage=targetUsage, description=targetSummary, type=attackType)
        db.session.add(attack)
        db.session.commit()
        logger.info('\n[MAIN] /upload/code - upload file SUCCESS')
        return "OK"
    else:
        logger.warning("\n[MAIN] /upload/code - upload file FAIL; that filename already exists")
        return "FAIL"
        
        
        

@bp.route('/<string:html>')
def convert_html(html):
    #print("[**]",html)
    if ".html" in html:
        return render_template(html.split('.')[0]+".html")
    return render_template(html+".html")


@bp.route('/utilities-other.html')
def utilities():
    return render_template('utilities-other.html')


# @bp.route('/report/<int:agentId>', methods=["POST"])
# def report(agentId):
#     try:
#         if request.method == 'POST':
#             data = request.get_json()
#             pkts = data["pkts"]
#             print("agentId : ", agentId)
#             print("pkts : ", pkts)
#             # pkts가 binary로 오던데 어떻게 받을 것인가. 오는 형태를 봐야할 듯.
#             try:
#                 link = data["link"]
#                 print("link : ", link)
#                 attackName = link.split('/')[-1]
#                 attackName = attackName.split('.')[0]

#                 crawled_description = crawler.crawl(attackName)
#                 if crawled_description == None:
#                     #return "crawling error!"
#                     print("crawling error!")
#                     return {"result":"good"}
#                 else:
#                     #return crawled_description
#                     print(crawled_description)
#                     return {"result":"good"}
#             except:
#                 pass
#             # 프론트로 어떻게 리턴할 것인지는 아직
#         return {"result":"good"}
#     except Exception as e:
#         print('report Error : ',e)
#         return





####################################################################################
############## FOR TEST ##############################################################
@bp.route('/insert/db', methods=['POST'])
def insert_into_db():
    try:
        if request.method=='POST':
            data = request.get_json()
            print(data)
            print(data["program"], data["version"], data["port"], data["fileName"], data["usage"], data["description"])
            attack = Attack(program=data["program"], version=data["version"], port=data["port"], fileName=data["fileName"], usage=data["usage"], description=data["description"])
            db.session.add(attack)
            db.session.commit()
            return {"result":True}
            
    except Exception as e:
        print('insert db Error : ', e)
        return False






@bp.route('/duu', methods=['POST'])
def dumm():
    if request.method=='POST':
        data = request.get_data()
        print('data : ', data)
        return