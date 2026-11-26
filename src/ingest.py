"""Load CSVs into PostgreSQL if DATABASE_URL is set, else SQLite (local fallback).
Schema is in sql/schema.sql. Usage: python -m src.ingest  (or DATABASE_URL=... python -m src.ingest)"""
import csv, os, sqlite3
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
TABLES={"vendors":("vendors.csv",5),"incidents":("incidents.csv",7),"damage_costs":("damage_costs.csv",5),"audits":("audits.csv",8)}
def main():
    url=os.environ.get("DATABASE_URL")
    if url:
        import psycopg2
        conn=psycopg2.connect(url); cur=conn.cursor()
        cur.execute((ROOT/"sql/schema.sql").read_text())
        for table,(fn,_) in TABLES.items():
            with open(ROOT/"data"/fn) as f:
                cur.copy_expert(f"COPY {table} FROM STDIN WITH CSV HEADER", f)
        conn.commit(); print("loaded to PostgreSQL"); return
    db=ROOT/"analysis/vendor_damage.sqlite"; db.parent.mkdir(exist_ok=True)
    conn=sqlite3.connect(db); cur=conn.cursor()
    cur.executescript((ROOT/"sql/schema.sql").read_text().replace("SERIAL","INTEGER").replace("NUMERIC(10,2)","REAL").replace("DATE","TEXT"))
    for table,(fn,n) in TABLES.items():
        cur.execute(f"DELETE FROM {table}")
        with open(ROOT/"data"/fn) as f:
            rows=list(csv.reader(f)); cur.executemany(f"INSERT INTO {table} VALUES ({','.join('?'*n)})", rows[1:])
    conn.commit(); print(f"loaded to SQLite fallback: {db} ({sum(1 for _ in open(ROOT/'data/incidents.csv'))-1} incidents)")
if __name__=="__main__": main()
