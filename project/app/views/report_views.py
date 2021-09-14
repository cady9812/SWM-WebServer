from flask import Blueprint, request, render_template

import base64


from app.models import Report
from app.modules import parser, loggers, statusCode
from app import db

logger = loggers.create_logger(__name__)



bp = Blueprint('report', __name__, url_prefix='/report')


@bp.route('/')
def report():
    reports = Report.query.with_entities(Report.no, Report.attackId, Report.startTime).order_by(Report.no.desc())
    dict_report = {}
    for report in reports:
        report_no = report[0]
        report_attackId = report[1]
        report_startTime = report[2]
        if report_no not in dict_report.keys():
            dict_report[report_no]=[[report_attackId], report_startTime]
        else:
            dict_report[report_no][0].append(report_attackId)
    arranged_reports = []
    for d in dict_report.keys():
        arranged_reports.append({
            "no":d,
            "attack_id":dict_report[d][0],
            "start_time":dict_report[d][1]
        })
    # print(arranged_reports)
    logger.info(f"[REPORT] GET ALL REPORTS")
    return render_template("report.html", sql_data = {
	    "data":arranged_reports
    })


@bp.route('/<int:reportNo>')
def show_one_report(reportNo):
    reports = Report.query.filter(Report.no==reportNo).all()
    arranged_reports = []
    for report in reports:
        arranged_reports.append({
            "no":report.no,
            "attack_id":report.attackId,
            "time":report.startTime,
            "log":report.log
        })
    logger.info(f"[REPORT] ONE REPORT IN DETAIL")
    return {
        "data":arranged_reports
    }