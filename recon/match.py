"""Match internal trades with broker confirmations and classify every break."""
from collections import Counter

PRICE_TOLERANCE_ORE = 100


def reconcile(internal, broker):
    by_id = {}
    seen = Counter(b["trade_id"] for b in broker)
    for b in broker:
        by_id.setdefault(b["trade_id"], b)
    breaks, matched = [], 0
    internal_ids = set()
    for t in internal:
        internal_ids.add(t["trade_id"])
        b = by_id.get(t["trade_id"])
        if b is None:
            breaks.append({"trade_id": t["trade_id"], "kind": "missing_at_broker", "detail": "no confirmation from broker"})
            continue
        problems = []
        if t["qty"] != b["qty"]:
            problems.append(("quantity_mismatch", f"internal {t['qty']} vs broker {b['qty']}"))
        if abs(t["price_ore"] - b["price_ore"]) > PRICE_TOLERANCE_ORE:
            problems.append(("price_mismatch", f"internal {t['price_ore']} vs broker {b['price_ore']} ore"))
        for kind, detail in problems:
            breaks.append({"trade_id": t["trade_id"], "kind": kind, "detail": detail})
        if not problems:
            matched += 1
    for tid, b in by_id.items():
        if tid not in internal_ids:
            breaks.append({"trade_id": tid, "kind": "missing_internal", "detail": "broker confirmed a trade we do not have"})
    for tid, n in seen.items():
        if n > 1:
            breaks.append({"trade_id": tid, "kind": "duplicate", "detail": f"broker sent {n} confirmations"})
    return {"matched": matched, "breaks": breaks, "internal": len(internal), "broker_rows": len(broker)}
