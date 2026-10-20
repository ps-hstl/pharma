"""Load CSVs into SQLite and run every query in sql/ (outputs saved to reports/sql_results/)."""
import sqlite3, pandas as pd
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
db = ROOT/"data"/"pharmapulse.db"
if db.exists(): db.unlink()
con = sqlite3.connect(db)
for f in (ROOT/"data"/"raw").glob("*.csv"):
    pd.read_csv(f).to_sql(f.stem, con, index=False)
con.executescript("CREATE INDEX ix_v ON visits(doctor_id); CREATE INDEX ix_s ON sales(doctor_id);")
out = ROOT/"reports"/"sql_results"; out.mkdir(exist_ok=True)
for q in sorted((ROOT/"sql").glob("*.sql")):
    df = pd.read_sql(q.read_text(), con)
    df.to_csv(out/f"{q.stem}.csv", index=False)
    print(f"\n=== {q.stem} ===\n{df.head(8).to_string(index=False)}")
