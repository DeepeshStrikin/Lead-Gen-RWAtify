import pandas as pd
import json

try:
    df = pd.read_excel('data/rwatify_leads.xlsx', sheet_name=None, header=None)
    output = {}
    for name, sheet in df.items():
        if 'Phase' in name:
            output[name] = sheet.head(5).fillna("").values.tolist()
            
    with open('data/inspect_rows.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2)
    print("Successfully wrote to data/inspect_rows.json")
except Exception as e:
    print(f'Error: {e}')
