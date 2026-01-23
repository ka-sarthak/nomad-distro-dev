import json
import pandas as pd
import pyarrow as pa

with open(
    "testing/export_entries_2026-01-21T15-25-52.165701+00-00/merged.json",
    "r",
    encoding="utf-8",
) as f:
    entry_list = json.load(f)

df = pd.json_normalize(entry_list)
table = pa.Table.from_pandas(df)

with pa.parquet.ParquetWriter(
    "testing/export_entries_2026-01-21T15-25-52.165701+00-00/merged.parquet",
    table.schema,
) as pq_writer:
    pq_writer.write_table(table)

print("Parquet file created successfully.")
