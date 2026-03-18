import os
import pandas as pd

RAW_DIR = "raw_clients_data"
OUTPUT_FILE = "old_all_data.xlsx"

def find_header_row(df):
    for idx, row in df.iterrows():
        row_str = " ".join([str(val).upper() for val in row.values if pd.notna(val)])
        if "COMPANY" in row_str or "ACCOUNT" in row_str or "NAME" in row_str or "DECISION" in row_str:
            # ensure it has at least a few columns to avoid false positive
            if len([v for v in row.values if pd.notna(v) and str(v).strip()]) > 2:
                return idx
    return 0

all_data = []

for file in os.listdir(RAW_DIR):
    if not file.endswith('.xlsx') or file.startswith("~"):
        continue
    filepath = os.path.join(RAW_DIR, file)
    print(f"Reading: {file}...")
    try:
        xl_raw = pd.ExcelFile(filepath)
        for sheet in xl_raw.sheet_names:
            if any(x in sheet.lower() for x in ["reject", "competitor", "summary"]):
                continue
                
            df_raw = xl_raw.parse(sheet, header=None)
            if df_raw.empty:
                continue

            header_idx = find_header_row(df_raw)
            headers = df_raw.iloc[header_idx].astype(str).str.strip()
            
            # replace NaN or blank titles with 'Unnamed_X'
            new_headers = []
            for i, h in enumerate(headers):
                if pd.isna(h) or h.lower() in ["nan", "none", ""]:
                    new_headers.append(f"Unnamed_{i}")
                else:
                    new_headers.append(h)
                    
            df_raw.columns = new_headers
            df_raw = df_raw.iloc[header_idx + 1:].reset_index(drop=True)
            
            # Identify columns that denote Company and Decision Maker
            company_col = None
            for col in new_headers:
                c = col.upper()
                if c in ["COMPANY NAME", "ACCOUNT", "NAME", "COMPANY"]:
                    company_col = col
                    break
            
            dm_col = None
            for col in new_headers:
                c = col.upper()
                if "DECISION MAKER" in c or c in ["CONTACT NAME", "EXEC NAME", "NAME"]:
                    if col != company_col:
                        dm_col = col
                        break
                    
            for _, row in df_raw.iterrows():
                row_dict = row.dropna().to_dict()
                if not row_dict:
                    continue
                    
                # Clean up any trailing spaces in keys
                row_dict = {str(k).strip(): v for k, v in row_dict.items() if not str(k).startswith("Unnamed_")}
                
                # Retrieve canonical values
                comp_val = str(row_dict.get(company_col, "")).strip() if company_col else ""
                dm_val = str(row_dict.get(dm_col, "")).strip() if dm_col else ""
                
                # Fallbacks for company name
                if not comp_val:
                    for k, v in row_dict.items():
                        if "COMPANY" in str(k).upper():
                            comp_val = str(v).strip()
                            break

                # Discard row if there is no company name found at all
                if not comp_val or len(comp_val) < 2:
                    continue

                row_dict["__Canonical_Company__"] = comp_val
                row_dict["__Canonical_DM__"] = dm_val
                row_dict["Source File"] = file
                row_dict["Source Sheet"] = sheet
                all_data.append(row_dict)
                
    except Exception as e:
        print(f"  -> Error on {file}: {e}")

df_all = pd.DataFrame(all_data)

if not df_all.empty:
    print(f"Total raw leads extracted: {len(df_all)}")
    
    # 1. Flag records that have a decision maker
    df_all['has_dm'] = df_all['__Canonical_DM__'].apply(lambda x: 0 if pd.isna(x) or str(x).strip() in ["", "nan"] else 1)
    
    # 2. Sort so that we keep the record WITH the decision maker when deduping
    df_all = df_all.sort_values(by=['has_dm', '__Canonical_Company__'], ascending=[False, True])
    
    # 3. Deduplicate based on cleaned company name
    df_all['Company_Norm'] = df_all['__Canonical_Company__'].str.lower().str.replace(r'[^a-z0-9]', '', regex=True)
    df_clean = df_all.drop_duplicates(subset=['Company_Norm'], keep='first').copy()
    
    print(f"Total unique companies after deduplication: {len(df_clean)}")
    
    # Clean up temp columns and split
    phase1_df = df_clean[df_clean["__Canonical_DM__"] != ""].copy()
    phase2_df = df_clean[df_clean["__Canonical_DM__"] == ""].copy()
    
    drop_cols = ['has_dm', 'Company_Norm', '__Canonical_Company__', '__Canonical_DM__']
    phase1_df = phase1_df.drop(columns=[c for c in drop_cols if c in phase1_df.columns])
    phase2_df = phase2_df.drop(columns=[c for c in drop_cols if c in phase2_df.columns])
    
    # Drop completely empty columns
    phase1_df = phase1_df.dropna(axis=1, how='all')
    phase2_df = phase2_df.dropna(axis=1, how='all')

    print(f"  -> Phase 1 (With Decision Maker): {len(phase1_df)}")
    print(f"  -> Phase 2 (Need to find contact): {len(phase2_df)}")
    
    with pd.ExcelWriter(OUTPUT_FILE, engine='openpyxl') as writer:
        if not phase1_df.empty:
            phase1_df.to_excel(writer, sheet_name='Phase 1', index=False)
        if not phase2_df.empty:
            phase2_df.to_excel(writer, sheet_name='Phase 2', index=False)
        
    print(f"\n✅ All clean leads have been saved to: {OUTPUT_FILE}")
else:
    print("No valid leads found.")
