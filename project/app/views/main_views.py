from flask import Blueprint, request
from flask.templating import render_template
from app.models import Attack
from app import redis_client, db
import os

from app.modules import loggers, statusCode
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
    return render_template('index.html')

# Show MITRE ATT&CK matrix
@bp.route('/upload')
def matrix():
    return render_template('./upload-code.html')

# Upload  Customed Attack file from User
@bp.route('/upload/file',methods=['POST'])
def upload():
    if request.method == 'GET':
        logger.warning(f"{loggers.RED}[MAIN] NOT GET{loggers.END}")
        return {"status":statusCode.METHOD_ERROR}
    
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

    logger.info(f"[MAIN] {fileName}\ntargetName : {targetName}\ntargetVersion : {targetVersion}\ntargetPort : {targetPort}\ntargetUsage : {targetUsage}\ntargetSummary : {targetSummary}\nattackType : {attackType}")

    if Attack.query.filter(Attack.fileName==fileName).first()==None:
        file.save(os.path.join(os.getcwd(), "attack_files", f"{fileName}"))
        
        attack = Attack(fileName=fileName, program=targetName, version=targetVersion, port=targetPort, usage=targetUsage, description=targetSummary, type=attackType)
        db.session.add(attack)
        db.session.commit()
        logger.info('[MAIN] UPLOAD SUCCESS')
        return {"status":statusCode.OK}
    else:
        logger.warning("{RED}[MAIN] UPLOAD FAIL; that filename already exists{END}")
        return {"status":statusCode.SERVER_ERROR}
        
        
        

@bp.route('/<string:html>')
def convert_html(html):
    #print("[**]",html)
    if ".html" in html:
        return render_template(html.split('.')[0]+".html")
    return render_template(html+".html")


@bp.route('/utilities-other.html')
def utilities():
    return render_template('utilities-other.html')





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