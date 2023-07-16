from fastapi import FastAPI
import json
from datetime import datetime

from process.create_tables import create_tables
from process.insert_report import insert_report
from process.get_report import get_reports
from process.insert_balance import insert_balance, insert_balance_with_timestamp
from process.get_balance import get_balance
from process.models import Report, Balance, BalanceWithTimestamp

app = FastAPI()

CONFIG_PATH = "data/config.json"

with open(CONFIG_PATH) as config_file:
    config = json.load(config_file)

database_name = config["server_settings"]["database_name"]


@app.on_event("startup")
async def startup_event():
    create_tables(database_name)


@app.post("/api/report")
async def report(report: Report):
    insert_report(report, database_name)
    return {"message": "Data received"}


@app.get("/api/report")
async def fetch_report():
    return get_reports(database_name)


@app.post("/api/balance")
async def submit_balance(balance: Balance):
    timestamp = datetime.utcnow().isoformat() + 'Z'

    insert_balance(balance.total_tokens, timestamp, database_name)

    return {"message": "Balance submitted"}


@app.post("/api/balance_with_timestamp")
async def submit_balance_with_timestamp(balance: BalanceWithTimestamp):
    insert_balance_with_timestamp(balance.total_tokens, balance.timestamp,
                                  database_name)

    return {"message": "Balance submitted with timestamp"}


@app.get("/api/balance")
async def get_latest_balance():
    balance_data = get_balance(database_name)

    return {"balance": balance_data["balance"],
            "timestamp": balance_data["timestamp"]}