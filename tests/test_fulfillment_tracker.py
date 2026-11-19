import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

import pytest
from backend.app.agents.fulfillment_tracker import fulfillment_tracker, ShipmentTracking

def test_fulfillment_tracker_lifecycle():
    order_id = "8PY1234567890"
    capture_id = "CAP-SIM-987654321"
    item_name = "Zebronics Zeb-Sound Feast 500 Portable Bluetooth Speaker"
    merchant = "Reliance Digital Verified"

    shipment = fulfillment_tracker.create_shipment(
        order_id=order_id,
        paypal_capture_id=capture_id,
        item_name=item_name,
        merchant_name=merchant,
        delivery_sla_str="1 Day (Next-Day Guaranteed)"
    )

    assert isinstance(shipment, ShipmentTracking)
    assert shipment.order_id == order_id
    assert shipment.paypal_capture_id == capture_id
    assert shipment.item_name == item_name
    assert shipment.merchant_name == merchant
    assert shipment.current_status == "IN_TRANSIT"
    assert shipment.progress_pct > 50
    assert len(shipment.tracking_number) > 10
    assert len(shipment.security_seal_hash) == 16
    assert len(shipment.milestones) == 4
    assert shipment.milestones[0].status == "COMPLETED"
    assert shipment.milestones[1].status == "COMPLETED"
    assert shipment.milestones[2].status == "IN_PROGRESS"
    assert shipment.milestones[3].status == "PENDING"
