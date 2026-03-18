import os
import pandas as pd
import json

RAW_DIR = "raw_clients_data"
MAIN_FILE = "data/rwatify_leads.xlsx"

out = {}
try:
    xl = pd.ExcelFile(MAIN_FILE)
    out["MAIN"] = {s: list(xl.parse(s).columns) for s in xl.sheet_names}
except Exception as e:
    out["MAIN"] = str(e)

out["RAW"] = {}
for file in os.listdir(RAW_DIR):
    if file.endswith('.xlsx'):
        try:
            xl_raw = pd.ExcelFile(os.path.join(RAW_DIR, file))
            out["RAW"][file] = {}
            for sheet in xl_raw.sheet_names:
                df = xl_raw.parse(sheet)
                out["RAW"][file][sheet] = f"{len(df)} rows, cols: {list(df.columns)}"
        except Exception as e:
            out["RAW"][file] = str(e)

with open("temp_headers.json", "w", encoding="utf-8") as f:
    json.dump(out, f, indent=2)
print("Done")
