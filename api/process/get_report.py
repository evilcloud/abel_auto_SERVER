import sqlite3
import json
from process.models import Report, Balance

def get_reports(database_name):
    with sqlite3.connect(database_name) as conn:
        c = conn.cursor()

        # Fetch all reports
        c.execute("SELECT * FROM rig")
        reports = c.fetchall()

        # # Parse the 'gpus' field back into a list
        # for report in reports:
        #     report['gpus'] = json.loads(report['gpus'])

        return reports
