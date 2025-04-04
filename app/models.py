from pydantic import BaseModel
from typing import List, Dict


class TransactionAnalysisResult(BaseModel):
    top_senders: List[Dict]
    top_receivers: List[Dict]
