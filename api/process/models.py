from pydantic import BaseModel
from typing import List, Optional

class Report(BaseModel):
  server_name: str
  gpus: List[str] = None
  hashrate_mh: float = None
  power_w: float = None

class Balance(BaseModel):
  total_tokens: float
  timestamp: Optional[str] = None

class BalanceWithTimestamp(BaseModel):
  total_tokens: float
  timestamp: str