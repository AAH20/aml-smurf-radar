"""
FinCEN Suspicious Activity Report (SAR) XML/JSON Generator.
Synthesizes regulatory narrative summaries and FinCEN BSA E-Filing XML payloads.
"""

from typing import List
import uuid
import time
from .models import SmurfCluster, FinCEN_SAR_Report

class FinCENSARGenerator:
    def generate_sar_report(self, cluster: SmurfCluster, primary_suspect_id: str) -> FinCEN_SAR_Report:
        """
        Synthesizes an automated FinCEN SAR filing document.
        """
        senders = list(set(t.sender_id for t in cluster.transactions))
        tx_count = len(cluster.transactions)

        narrative = (
            f"Automated AML Smurf Radar detected structured activity on account {primary_suspect_id}. "
            f"Over a duration of {cluster.duration_seconds:.1f} seconds, the subject account received "
            f"{tx_count} distinct micro-transactions aggregating to ${cluster.total_aggregated_amount:,.2f} USD "
            f"from {cluster.sender_count} distinct counterparty accounts. Transaction amounts ranged between "
            f"${min(t.amount for t in cluster.transactions):,.2f} and ${max(t.amount for t in cluster.transactions):,.2f}, "
            f"exhibiting classic smurfing typology designed to circumvent Bank Secrecy Act (BSA) $10,000 CTR thresholds."
        )

        xml_payload = f"""<?xml version="1.0" encoding="UTF-8"?>
<FinCEN_BSA_SAR version="2.0">
    <FilingHeader>
        <ReportID>SAR_{uuid.uuid4().hex[:12].upper()}</ReportID>
        <Timestamp>{time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}</Timestamp>
        <FilingInstitution>A2Z SOC Regulated FinTech Enclave</FilingInstitution>
    </FilingHeader>
    <SuspiciousActivity>
        <Typology>STRUCTURING_SMURFING_BSA_CTR_EVASION</Typology>
        <TotalAmount Currency="USD">{cluster.total_aggregated_amount:.2f}</TotalAmount>
        <PrimarySubject>{primary_suspect_id}</PrimarySubject>
        <AssociatedCounterpartiesCount>{len(senders)}</AssociatedCounterpartiesCount>
        <Narrative>{narrative}</Narrative>
    </SuspiciousActivity>
</FinCEN_BSA_SAR>"""

        return FinCEN_SAR_Report(
            sar_id=f"sar_{uuid.uuid4().hex[:12]}",
            cluster_id=cluster.cluster_id,
            primary_suspect=primary_suspect_id,
            associated_entities=senders,
            total_amount=cluster.total_aggregated_amount,
            structuring_typology="STRUCTURING_SMURFING_BSA_CTR_EVASION",
            narrative=narrative,
            generated_at=time.time(),
            fincen_xml_payload=xml_payload
        )
