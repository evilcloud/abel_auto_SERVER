from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime
import sqlite3
import os
import json

app = FastAPI()

CONFIG_PATH = os.environ.get("CONFIG_PATH", "data/config.json")

# Load the configuration file
with open(CONFIG_PATH) as config_file:
    config = json.load(config_file)

DATABASE_PATH = os.path.join("data", config["server_settings"]["database_name"])
LOGFILE_PATH = os.path.join("data", config["server_settings"]["logfile_name"])


class Report(BaseModel):
    server_name: str
    gpus: list[str] = None
    hashrate_mh: float = None
    power_w: float = None


def create_rig_table():
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS rig (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            gpus TEXT,
            hashrate_mh INTEGER,
            power_w INTEGER,
            created_at TIMESTAMP
        )
        """
    )
    conn.commit()
    conn.close()


def log_transaction(message):
    with open(LOGFILE_PATH, "a") as file:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        file.write(f"{timestamp}: {message}\n")


@app.post("/api/report")
def report(report: Report):
    rig_name = report.server_name
    gpus = json.dumps(report.gpus) if report.gpus else ''

    hashrate = 0
    power = 0

    try:
        hashrate = int(report.hashrate_mh)
    except (ValueError, TypeError):
        hashrate = 0

    try:
        power = int(report.power_w)
    except (ValueError, TypeError):
        power = 0

    if not rig_name:
        log_transaction("Invalid report: Missing rig name")
        raise HTTPException(status_code=400, detail="Rig name is required")

    create_rig_table()
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    c.execute(
        """
        INSERT INTO rig (name, gpus, hashrate_mh, power_w, created_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        (rig_name, gpus, hashrate, power, datetime.now()),
    )
    conn.commit()
    conn.close()

    log_transaction("Data received")

    return {"message": "Data received"}


@app.get("/api/report")
def get_report():
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM rig")
    rows = c.fetchall()
    conn.close()

    return rows
