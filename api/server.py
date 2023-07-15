from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from datetime import datetime
import os
import json
from sqlalchemy import create_engine, Table, MetaData, Column, Integer, String, DateTime, Float, select
from typing import Optional, List

app = FastAPI()

CONFIG_PATH = os.environ.get("CONFIG_PATH", "data/config.json")

# Load the configuration file
with open(CONFIG_PATH) as config_file:
    config = json.load(config_file)

DATABASE_PATH = os.path.join("data", config["server_settings"]["database_name"])
LOGFILE_PATH = os.path.join("data", config["server_settings"]["logfile_name"])
MAX_TIMEOUT = 600

class Report(BaseModel):
    server_name: str
    gpus: Optional[List[str]] = Field(default=None)
    hashrate_mh: Optional[float] = Field(default=None)
    power_w: Optional[float] = Field(default=None)

class Balance(BaseModel):
    balance: float
    timestamp: Optional[datetime] = Field(default=None)

# create database engine
engine = create_engine(f'sqlite:///{DATABASE_PATH}', echo = True)

metadata = MetaData()

rigs = Table(
    'rig', metadata,
    Column('id', Integer, primary_key=True),
    Column('name', String),
    Column('num_gpus', Integer),
    Column('gpu_names', String),
    Column('hashrate_mh', Float),
    Column('power_w', Float),
    Column('updated_at', DateTime),
)

balances = Table(
    'balance', metadata,
    Column('id', Integer, primary_key=True),
    Column('balance', Float),
    Column('timestamp', DateTime),
)

# create tables if they do not exist
with engine.connect() as connection:
    metadata.create_all(connection)

@app.post("/api/report")
async def report(report: Report):
    with engine.connect() as connection:
        ins = rigs.insert().values(
            name=report.server_name,
            num_gpus=len(report.gpus) if report.gpus else 0,
            gpu_names=','.join(report.gpus) if report.gpus else '',
            hashrate_mh=report.hashrate_mh,
            power_w=report.power_w,
            updated_at=datetime.now()
        )
        result = connection.execute(ins)
    return {"message": "Data received"}

@app.get("/api/report")
async def get_report():
    with engine.connect() as connection:
        s = select(rigs)
        result = connection.execute(s)
        data = [dict(row) for row in result]
    return data
@app.post("/api/balance")
async def submit_balance(balance: Balance):
    with engine.connect() as connection:
        ins = balances.insert().values(
            balance=balance.balance,
            timestamp=balance.timestamp or datetime.now()
        )
        result = connection.execute(ins)
    return {"message": "Balance received"}

@app.get("/api/balance")
async def get_balance():
    with engine.connect() as connection:
        s = balances.select()
        result = connection.execute(s)
    return [dict(row) for row in result]
