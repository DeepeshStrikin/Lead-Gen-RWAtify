import pandas as pd
import json

try:
    df = pd.read_excel('data/rwatify_leads.xlsx', sheet_name=None)
    output = {}
    for name, sheet in df.items():
        date_cols = [c for c in sheet.columns if 'date' in str(c).lower()]
        sample_dates = sheet[date_cols[0]].dropna().astype(str).head(5).tolist() if date_cols else []
        
        output[name] = {
            'columns': list(sheet.columns),
            'total_rows': len(sheet),
            'date_columns': date_cols,
            'sample_dates': sample_dates
        }
    
    with open('data/explore_leads.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2)
    print("Successfully wrote to data/explore_leads.json")
except Exception as e:
    print(f'Error: {e}')
