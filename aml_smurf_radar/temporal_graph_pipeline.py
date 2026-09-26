"""
Temporal graph ingestion pipeline.
Constructs in-memory directed temporal transaction graphs across multi-rail feeds.
"""

from typing import List, Dict
from collections import defaultdict
from .models import TransactionNode

class TemporalGraphPipeline:
    def __init__(self, time_window_seconds: float = 3600.0):
        self.time_window = time_window_seconds
        self.transactions: List[TransactionNode] = []
        # Adjacency maps
        self.outbound_graph: Dict[str, List[TransactionNode]] = defaultdict(list)
        self.inbound_graph: Dict[str, List[TransactionNode]] = defaultdict(list)

    def ingest_transaction(self, tx: TransactionNode) -> None:
        """Adds transaction to graph and indexes sender/recipient nodes."""
        self.transactions.append(tx)
        self.outbound_graph[tx.sender_id].append(tx)
        self.inbound_graph[tx.recipient_id].append(tx)

    def get_inbound_transactions(self, recipient_id: str) -> List[TransactionNode]:
        return self.inbound_graph.get(recipient_id, [])

    def get_outbound_transactions(self, sender_id: str) -> List[TransactionNode]:
        return self.outbound_graph.get(sender_id, [])
