from flask import Blueprint, request
from app import redis_client

import json
import logging
import logging.config
import pathlib
log_config = (pathlib.Path(__file__).parent.resolve().parents[1].joinpath("log_config.json"))
config = json.load(open(str(log_config)))
logging.config.dictConfig(config)
logger = logging.getLogger(__name__)


bp = Blueprint('agent', __name__, url_prefix='/agent')

@bp.route('/add', methods=['POST'])
def add_agent():
    if request.method=='GET':
        logger.warning('[AGENT] /add - NOT GET Method')
        return
    agent_ip = request.get_json()['ip']
    redis_client.sadd("agents",agent_ip)
    logger.info(f"[AGENT] ADD / IP :{agent_ip}")
    return

@bp.route('/del', methods=['POST'])
def del_agent():
    if request.method=='GET':
        logger.warning('[AGENT] /del - Not GET Method')
        return
    agent_ip = request.get_json()['ip']
    redis_client.srem("agents", agent_ip)
    logger.info(f"[AGENT] DEL / IP :{agent_ip}")
    return


@bp.route('/show')
def show_agent():
    all_agents = redis_client.smembers("agents")
    # all_agents = {b'2.2.2.2', b'1.1.1.1'}
    all_agents = [a.decode() for a in all_agents]
    # ['2.2.2.2', '1.1.1.1']
    logger.info(f'[AGENT] SHOW / {all_agents}')
    return


    

