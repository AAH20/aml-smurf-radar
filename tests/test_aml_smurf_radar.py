"""
Unit tests for aml-smurf-radar.
Verifies temporal graph ingestion, fan-in smurfing detection, and SAR XML generation.
"""

import unittest
import time
from aml_smurf_radar.models import TransactionNode, ChannelType
from aml_smurf_radar.temporal_graph_pipeline import TemporalGraphPipeline
from aml_smurf_radar.structuring_detector import StructuringDetector
from aml_smurf_radar.fincen_sar_generator import FinCENSARGenerator
from aml_smurf_radar.a2zsoc_aml_bridge import A2ZSOCAMLBridge

class TestAMLSmurfRadar(unittest.TestCase):
    def setUp(self):
        self.pipeline = TemporalGraphPipeline()
        self.detector = StructuringDetector(min_cluster_transactions=3)
        self.sar_gen = FinCENSARGenerator()
        self.bridge = A2ZSOCAMLBridge()

    def test_smurf_detection_success(self):
        now = time.time()
        collector = "target_wallet"
        txs = [
            TransactionNode(tx_id="t1", sender_id="s1", recipient_id=collector, amount=300.0, channel=ChannelType.MOBILE_WALLET_CASH, timestamp=now-30),
            TransactionNode(tx_id="t2", sender_id="s2", recipient_id=collector, amount=350.0, channel=ChannelType.RETAIL_POS_FAWRY, timestamp=now-20),
            TransactionNode(tx_id="t3", sender_id="s3", recipient_id=collector, amount=400.0, channel=ChannelType.CRYPTO_STABLECOIN_BRIDGE, timestamp=now-10),
            TransactionNode(tx_id="t4", sender_id="s4", recipient_id=collector, amount=5000.0, channel=ChannelType.ACH_P2P, timestamp=now)
        ]
        for t in txs:
            self.pipeline.ingest_transaction(t)

        cluster = self.detector.analyze_fan_in_cluster(collector, self.pipeline)
        self.assertIsNotNone(cluster)
        self.assertTrue(cluster.is_smurfing)
        self.assertEqual(cluster.sender_count, 4)
        self.assertEqual(cluster.total_aggregated_amount, 6050.0)

        # SAR Generation
        sar = self.sar_gen.generate_sar_report(cluster, collector)
        self.assertIn("STRUCTURING_SMURFING", sar.structuring_typology)
        self.assertIn("<FinCEN_BSA_SAR", sar.fincen_xml_payload)

        # A2Z SOC Seal
        seal = self.bridge.anchor_aml_evidence(cluster, sar)
        self.assertTrue(seal.startswith("a2z_aml_seal_"))

    def test_no_smurfing_insufficient_senders(self):
        now = time.time()
        single_account = "recipient_clean"
        txs = [
            TransactionNode(tx_id="tx_a", sender_id="same_sender", recipient_id=single_account, amount=50.0, channel=ChannelType.ACH_P2P, timestamp=now-10),
            TransactionNode(tx_id="tx_b", sender_id="same_sender", recipient_id=single_account, amount=60.0, channel=ChannelType.ACH_P2P, timestamp=now)
        ]
        for t in txs:
            self.pipeline.ingest_transaction(t)

        cluster = self.detector.analyze_fan_in_cluster(single_account, self.pipeline)
        self.assertIsNone(cluster)

if __name__ == "__main__":
    unittest.main()
