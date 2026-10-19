"""Synthetic trading data. Invented for this project, not real customer data. Money is in ore (integers)."""
import random
from datetime import datetime, timedelta


def make_day(n_trades=400, seed=5):
    rng = random.Random(seed)
    internal, broker = [], []
    day = datetime(2026, 10, 19, 9, 0)
    for i in range(n_trades):
        t = {"trade_id": f"T{i:05d}", "client": f"C{rng.randint(1, 60):03d}", "isin": rng.choice(["DK0010244508", "US0378331005", "DK0060534915"]),
             "side": rng.choice(["BUY", "SELL"]), "qty": rng.randint(1, 200), "price_ore": rng.randint(5_000, 90_000),
             "traded_at": (day + timedelta(minutes=i)).isoformat(timespec="seconds")}
        internal.append(t)
        broker.append(dict(t))
    breaks = {"missing_at_broker": 5, "missing_internal": 4, "quantity_mismatch": 6, "price_mismatch": 5, "duplicate": 3}
    idx = rng.sample(range(n_trades), sum(breaks.values()))
    k = 0
    for kind, count in breaks.items():
        for _ in range(count):
            i = idx[k]; k += 1
            if kind == "missing_at_broker":
                broker[i] = None
            elif kind == "missing_internal":
                internal[i] = None
            elif kind == "quantity_mismatch":
                broker[i]["qty"] += rng.choice([-1, 1, 10])
            elif kind == "price_mismatch":
                broker[i]["price_ore"] += rng.choice([400, -700, 250])
            else:
                broker.append(dict(broker[i]))
    return [t for t in internal if t], [t for t in broker if t], breaks


def make_client_money(seed=5):
    rng = random.Random(seed)
    balances = {f"C{i:03d}": rng.randint(0, 5_000_000) for i in range(1, 61)}
    bank = sum(balances.values())
    return balances, bank


def make_cash_movements(seed=5):
    rng = random.Random(seed)
    base = datetime(2026, 10, 19, 8, 0)
    rows = []
    for i in range(300):
        rows.append({"client": f"C{rng.randint(1, 60):03d}", "kind": rng.choice(["deposit", "withdrawal"]),
                     "amount_ore": rng.randint(10_000, 3_000_000), "country": "DK",
                     "at": (base + timedelta(minutes=rng.randint(0, 60 * 24))).isoformat(timespec="seconds")})
    # planted patterns
    for j in range(4):
        rows.append({"client": "C900", "kind": "deposit", "amount_ore": 9_200_000 + j * 100_000, "country": "DK",
                     "at": (base + timedelta(hours=j)).isoformat(timespec="seconds")})
    rows.append({"client": "C901", "kind": "deposit", "amount_ore": 15_000_000, "country": "DK", "at": base.isoformat(timespec="seconds")})
    rows.append({"client": "C901", "kind": "withdrawal", "amount_ore": 14_500_000, "country": "DK",
                 "at": (base + timedelta(hours=5)).isoformat(timespec="seconds")})
    rows.append({"client": "C902", "kind": "deposit", "amount_ore": 500_000, "country": "IR", "at": base.isoformat(timespec="seconds")})
    return rows
