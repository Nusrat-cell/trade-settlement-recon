"""Client money check: what clients are owed must be covered by the segregated bank balance."""


def check(client_balances_ore, bank_balance_ore):
    owed = sum(client_balances_ore.values())
    gap = bank_balance_ore - owed
    return {"owed_ore": owed, "bank_ore": bank_balance_ore, "gap_ore": gap,
            "status": "ok" if gap >= 0 else "SHORTFALL", "negative_clients": sorted(c for c, v in client_balances_ore.items() if v < 0)}
