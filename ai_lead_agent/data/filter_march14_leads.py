import pandas as pd
import json
import ast

def get_missing_data(file_path):
    try:
        # Load Phase 1
        df_phase1 = pd.read_excel(file_path, sheet_name='⚡ Phase 1 — Contact Now', header=2)
        # Load Phase 2
        df_phase2 = pd.read_excel(file_path, sheet_name='🟡 Phase 2 — Nurture', header=2)
        
        missing_leads = []
        
        for phase, df in [('Phase 1', df_phase1), ('Phase 2', df_phase2)]:
            for i in range(len(df)):
                row = df.iloc[i]
                date_val = str(row.get('DATE', '')).lower()
                scraped_val = str(row.get('SCRAPED AT', '')).lower()
                
                # Check for any variation of March 14
                is_march_14 = any(x in date_val for x in ['14-03', '03-14', 'march 14', 'mar 14']) or \
                              any(x in scraped_val for x in ['14-03', '03-14', '2026-03-14'])
                
                if is_march_14:
                    company = str(row.get('COMPANY NAME', '')).strip()
                    if company.lower() in ['nan', 'none', '']: continue # Skip empty rows
                    
                    website = str(row.get('WEBSITE', '')).strip()
                    person_li = str(row.get('PERSON LINKEDIN', '')).strip()
                    dm = str(row.get('DECISION MAKER', '')).strip()
                    title = str(row.get('THEIR TITLE', 'CEO')).strip()
                    if title.lower() in ['nan', 'none', '']: title = "Decision Maker / CEO"
                    
                    needs_website = website.lower() in ['nan', 'none', '', 'http://nan', 'https://nan'] or 'google.com/search' in website.lower()
                    needs_linkedin = person_li.lower() in ['nan', 'none', '', 'http://nan', 'https://nan'] or 'google.com/search' in person_li.lower()
                    
                    if needs_website or needs_linkedin or dm.lower() in ['nan', 'none', '']:
                        lead_info = {
                            'Phase': phase,
                            'Excel_Row_Index': i + 4, # +2 for header offset, +1 for 0-index, +1 to match Excel row numbers = +4 total offset.
                            'Company': company,
                            'Title': title,
                            'Needs_Website': needs_website,
                            'Needs_LinkedIn': needs_linkedin,
                            'Current_Website': website,
                            'Current_DM': dm,
                            'Current_LinkedIn': person_li
                        }
                        missing_leads.append(lead_info)
        
        with open('data/missing_march14.json', 'w', encoding='utf-8') as f:
            json.dump(missing_leads, f, indent=2)
            
        print(f"Found {len(missing_leads)} leads needing research for March 14th.")
        
    except Exception as e:
        print(f"Error processing leads: {e}")

if __name__ == "__main__":
    get_missing_data('data/rwatify_leads.xlsx')
