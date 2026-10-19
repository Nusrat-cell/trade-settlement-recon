"""Usage: python -m recon demo"""
import sys
import tempfile
from collections import Counter
from pathlib import Path

from . import aml, client_money, gen, match, report

if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] != "demo":
        sys.exit("usage: python -m recon demo")
    internal, broker, planted = gen.make_day()
    rec = match.reconcile(internal, broker)
    money = client_money.check(*gen.make_client_money())
    alerts = aml.alerts(gen.make_cash_movements())
    out = Path(tempfile.mkdtemp()) / "daily_report.xlsx"
    report.write(out, rec, money, alerts)
    print("planted breaks:", planted)
    print("found breaks:", dict(Counter(b["kind"] for b in rec["breaks"])))
    print("matched:", rec["matched"], "of", rec["internal"])
    print("client money:", money["status"], money["gap_ore"])
    print("AML alerts:", dict(Counter(a["rule"] for a in alerts)))
    print("report:", out)
