"""Simple, readable AML alert rules. Thresholds are examples, not legal advice."""
from datetime import datetime, timedelta

LARGE_ORE = 10_000_000          # single movement of DKK 100,000 or more
STRUCTURING_BAND = (0.80, 1.00)  # deposits just under the large threshold
STRUCTURING_COUNT = 3
STRUCTURING_WINDOW = timedelta(hours=24)
PASS_THROUGH_SHARE = 0.90
PASS_THROUGH_WINDOW = timedelta(hours=48)
HIGH_RISK = {"IR", "KP", "MM"}


def _t(r):
    return datetime.fromisoformat(r["at"])


def alerts(rows):
    out = []
    by_client = {}
    for r in sorted(rows, key=_t):
        by_client.setdefault(r["client"], []).append(r)
        if r["amount_ore"] >= LARGE_ORE:
            out.append({"client": r["client"], "rule": "LARGE_MOVEMENT", "reason": f"{r['kind']} of {r['amount_ore']} ore"})
        if r["country"] in HIGH_RISK:
            out.append({"client": r["client"], "rule": "HIGH_RISK_COUNTRY", "reason": f"{r['kind']} linked to {r['country']}"})
    for client, items in by_client.items():
        deps = [r for r in items if r["kind"] == "deposit" and LARGE_ORE * STRUCTURING_BAND[0] <= r["amount_ore"] < LARGE_ORE * STRUCTURING_BAND[1]]
        for i, d in enumerate(deps):
            window = [x for x in deps[i:] if _t(x) - _t(d) <= STRUCTURING_WINDOW]
            if len(window) >= STRUCTURING_COUNT:
                out.append({"client": client, "rule": "STRUCTURING", "reason": f"{len(window)} deposits just under the limit within 24 hours"})
                break
        for d in [r for r in items if r["kind"] == "deposit"]:
            outflow = sum(w["amount_ore"] for w in items if w["kind"] == "withdrawal" and timedelta(0) <= _t(w) - _t(d) <= PASS_THROUGH_WINDOW)
            if d["amount_ore"] >= LARGE_ORE * 0.5 and outflow >= PASS_THROUGH_SHARE * d["amount_ore"]:
                out.append({"client": client, "rule": "PASS_THROUGH", "reason": "deposit mostly withdrawn within 48 hours"})
                break
    return out
