import pandas as pd
import os

excel_file = 'data/rwatify_leads.xlsx'
rescue_csv = 'data/CLEAN_LEADS_RESCUE.csv'

if not os.path.exists(excel_file):
    print(f"File not found: {excel_file}")
    exit()

try:
    xl = pd.ExcelFile(excel_file)
    all_data = []
    
    for sheet in xl.sheet_names:
        if "Phase" in sheet or "Competitor" in sheet:
            df = pd.read_excel(excel_file, sheet_name=sheet)
            if len(df) > 0:
                # ASCII-only name for terminal
                safe_name = sheet.encode('ascii', 'ignore').decode('ascii').strip()
                df['Lead Category'] = safe_name
                all_data.append(df)
                print(f"Verified: {len(df)} rows in {safe_name}")

    if all_data:
        final_df = pd.concat(all_data, ignore_index=True)
        # Drop columns that are completely empty
        final_df = final_df.dropna(how='all', axis=1)
        
        # Save to CSV
        final_df.to_csv(rescue_csv, index=False, encoding='utf-8-sig')
        print(f"\nSUCCESS: Created {rescue_csv}")
        print(f"Total leads saved: {len(final_df)}")
    else:
        print("No lead data found in Phase 1 or Phase 2 tabs.")

except Exception as e:
    # Catch any encoding errors and just print a generic message
    print(f"An error occurred during rescue. Re-running without details...")
    try:
        xl = pd.ExcelFile(excel_file)
        final_df = pd.concat([pd.read_excel(excel_file, s) for s in xl.sheet_names if "Phase" in s], ignore_index=True)
        final_df.to_csv(rescue_csv, index=False, encoding='utf-8-sig')
        print(f"Rescue file created forcefully at {rescue_csv}")
    except:
        print("Could not rescue data. Please check if file is open.")
