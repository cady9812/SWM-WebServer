import json
import logging
import logging.config
import pathlib
import logstash
log_config = (pathlib.Path(__file__).parent.resolve().parents[1].joinpath("log_config.json"))
config = json.load(open(str(log_config)))
logging.config.dictConfig(config)
#logger = logging.getLogger(__name__)

from private.ports import LOGSTASH_PORT

def create_logger(logger_name):
    logger = logging.getLogger(logger_name)
    # logger.addHandler(logstash.TCPLogstashHandler('localhost', 5001, version=1))
    logger.addHandler(logstash.TCPLogstashHandler('localhost', LOGSTASH_PORT, version=1))
    return logger
