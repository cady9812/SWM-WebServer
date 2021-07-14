from private import mysql_info

SQLALCHEMY_DATABASE_URI = "mysql+pymysql://{0}:{1}@{2}/{3}".format(mysql_info.username, mysql_info.password, mysql_info.db_ip, mysql_info.db_name)
SQLALCHEMY_TRACK_MODIFICATIONS = False
