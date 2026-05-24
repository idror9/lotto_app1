import streamlit as st
import pandas as pd
from collections import Counter
import random

st.set_page_config(page_title="לוטו חכם", layout="centered")

def parse_lotto_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf8') as f:
            lines = [line.strip() for line in f.readlines()]
        records = []
        current_record = {}
        i = 0
        while i < len(lines):
            line = lines[i]
            if "תאריך הגרלה:" in line:
                if current_record and 'תאריך' in current_record and 'מספרים' in current_record:
                    records.append(current_record)
                current_record = {'תאריך': lines[i+1]}
                i += 1
            elif "המספר החזק:" in line:
                try: current_record['חजק'] = int(lines[i+1])
                except: pass
                i += 1
            elif "המספרים שעלו בגורל:" in line:
                start = i + 1
                if start < len(lines) and lines[start] == "": start += 1
                nums = []
                for j in range(6):
                    if start + j < len(lines):
                        try: nums.append(int(lines[start+j]))
                        except: pass
                current_record['מספרים'] = nums
                i = start + 5
            i += 1
        if current_record and 'תאריך' in current_record and 'מספרים' in current_record:
            records.append(current_record)
        return records
    except:
        return None

records = parse_lotto_file('lotto2026.csv')

if records:
    # הפיכת הרשימה כדי לעבוד בסדר כרונולוגי מהישן לחדש
    records.reverse()
    
    next_strong_after_2 = []
    for i in range(len(records) - 1):
        if records[i].get('חזק') == 2:
            next_draw = records[i+1]
            if next_draw.get('חזק'):
                next_strong_after_2.append(next_draw['חזק'])
                
    total_cases = len(next_strong_after_2)
    counts_after_2 = Counter(next_strong_after_2)
    
    st.title("🎰 מחולל לוטו אסטרטגי מתוקן")
    
    st.subheader("📊 טבלת שכיחות: מספרים חזקים שעלו מיד אחרי המספר 2")
    st.write(f"המספר 2 הופיע כהגרלה קודמת {total_cases} פעמים לאורך השנה המלאה בקובץ.")
    
    if total_cases > 0:
        stats_data = []
        for i in range(1, 8):
            times = counts_after_2.get(i, 0)
            chance = (times / total_cases) * 100
            stats_data.append({
                "מספר חזק עוקב": i,
                "שכיחות (כמות פעמים)": times,
                "הסתברות סטטיסטית": f"{chance:.1f}%"
            })
            
        stats_df = pd.DataFrame(stats_data)
        st.dataframe(stats_df.set_index("מספר חזק עוקב"), use_container_width=True)
    else:
        st.info("לא נמצאו מספיק נתונים על הופעת המספר 2 בקובץ.")
        
    st.divider()
    
    # לוגיקת הגרלת הטורים (כפתור 1 וכפתור 2) נשארת כאן בהמשך הקוד...
