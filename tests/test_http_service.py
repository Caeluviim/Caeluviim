import json
from pathlib import Path

import caeluviim_graph.http_service as svc


def test_ingest_persists_event_and_receipt(tmp_path: Path):
    svc.DATA = tmp_path
    svc.EVENTS = tmp_path / "events.jsonl"
    svc.RECEIPTS = tmp_path / "receipts.jsonl"
    receipt = svc.ingest({"claim": "the repository executes"})
    assert receipt["result"] == "accepted"
    assert receipt["validation_result"] == "pass"
    assert len(receipt["receipt_hash"]) == 64
    event = json.loads(svc.EVENTS.read_text(encoding="utf-8").strip())
    stored = json.loads(svc.RECEIPTS.read_text(encoding="utf-8").strip())
    assert event["id"] == receipt["event_id"]
    assert stored == receipt
