"""
Algorithmic Structuring and Smurfing Detector.
Identifies high-frequency fan-in and fan-out clusters designed to evade BSA $10,000 CTR thresholds.
"""

from typing import List, Optional
import uuid
from .models import TransactionNode, SmurfCluster
from .temporal_graph_pipeline import TemporalGraphPipeline

class StructuringDetector:
    def __init__(self, min_cluster_transactions: int = 3, threshold_amount: float = 10000.0):
        self.min_txs = min_cluster_transactions
        self.ctr_threshold = threshold_amount

    def analyze_fan_in_cluster(
        self,
        recipient_id: str,
        graph: TemporalGraphPipeline,
        time_window_seconds: float = 3600.0
    ) -> Optional[SmurfCluster]:
        """
        Analyzes inbound transactions to an account.
        Detects multiple senders transferring micro-amounts to a single collector (Smurfing).
        """
        inbound = graph.get_inbound_transactions(recipient_id)
        if len(inbound) < self.min_txs:
            return None

        # Sort by timestamp
        sorted_txs = sorted(inbound, key=lambda x: x.timestamp)
        earliest = sorted_txs[0].timestamp
        latest = sorted_txs[-1].timestamp
        duration = max(1.0, latest - earliest)

        total_amount = sum(t.amount for t in sorted_txs)
        distinct_senders = len(set(t.sender_id for t in sorted_txs))

        # Calculate structuring score
        # Higher score if multiple senders, micro-amounts, and total approaches CTR threshold
        score = 0.20
        if distinct_senders >= 3:
            score += 0.30
        if any(100.0 <= t.amount <= 1000.0 for t in sorted_txs):
            score += 0.25  # Classic micro-smurfing amounts
        if total_amount >= 5000.0:
            score += 0.20  # High aggregated volume

        score = min(0.99, score)
        is_smurf = score >= 0.75 and distinct_senders >= 3

        return SmurfCluster(
            cluster_id=f"smurf_{uuid.uuid4().hex[:12]}",
            transactions=sorted_txs,
            total_aggregated_amount=round(total_amount, 2),
            sender_count=distinct_senders,
            recipient_count=1,
            duration_seconds=duration,
            structuring_score=round(score, 3),
            is_smurfing=is_smurf
        )
