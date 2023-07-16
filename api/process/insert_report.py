import sqlite3
import json
from process.models import Report

INSERT_REPORT = """
INSERT INTO rig (name, gpus, hashrate_mh, power_w, created_at)
VALUES (?, ?, ?, ?, datetime('now', 'utc'))
"""

def insert_report(report: Report, database_name):
    with sqlite3.connect(database_name) as conn:
        c = conn.cursor()

        # Convert the list of GPUs to a JSON string
        gpus_json = json.dumps(report.gpus)

        # Insert the report into the 'rig' table
        c.execute(INSERT_REPORT, (report.server_name, gpus_json, report.hashrate_mh, report.power_w))
