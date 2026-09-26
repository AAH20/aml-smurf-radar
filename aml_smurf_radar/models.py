"""
Data models for aml-smurf-radar.
Represents transaction nodes, topological smurf clusters, and FinCEN SAR payloads.
Uses pure standard library dataclasses for zero-dependency portability.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Any, Optional
import time
import hashlib

class ChannelType(str, Enum):
    RETAIL_POS_FAWRY = "RETAIL_POS_FAWRY"
    MOBILE_WALLET_CASH = "MOBILE_WALLET_CASH"
    CRYPTO_STABLECOIN_BRIDGE = "CRYPTO_STABLECOIN_BRIDGE"
    ACH_P2P = "ACH_P2P"
    SEPA_INSTANT = "SEPA_INSTANT"

@dataclass
class TransactionNode:
    tx_id: str
    sender_id: str
    recipient_id: str
    amount: float
    channel: ChannelType
    timestamp: float = field(default_factory=time.time)
    terminal_id: Optional[str] = None
    ip_address: Optional[str] = None

@dataclass
class SmurfCluster:
    cluster_id: str
    transactions: List[TransactionNode]
    total_aggregated_amount: float
    sender_count: int
    recipient_count: int
    duration_seconds: float
    structuring_score: float  # 0.00 to 1.00
    is_smurfing: bool

    def compute_sha256_hash(self) -> str:
        tx_ids = ",".join(t.tx_id for t in self.transactions)
        payload = f"{self.cluster_id}:{self.total_aggregated_amount}:{tx_ids}:{self.structuring_score}"
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

@dataclass
class FinCEN_SAR_Report:
    sar_id: str
    cluster_id: str
    primary_suspect: str
    associated_entities: List[str]
    total_amount: float
    structuring_typology: str
    narrative: str
    generated_at: float = field(default_factory=time.time)
    fincen_xml_payload: str = ""
