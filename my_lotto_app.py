import streamlit as st
import pandas as pd
from collections import Counter
import random
import re

# הגדרת דף נקייה והסתרת תפריטים מיותרים לנייד
st.set_page_config(page_title="לוטו חכם", layout="centered")

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stButton>button {width: 100%; border-radius: 20px; height: 3.5em; font-weight: bold; margin-bottom: 10px;}
    </style>
    """, unsafe_allow_html=True)

def parse_lotto_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf8') as f:
            lines = [line.strip() for line in f.readlines()]
        records = []
        current_record = {}
        i = 0
        while i < len(lines):
            line = lines[i]
            if "תאריך הגרלה:" in line or "תאריך:" in line:
                if current_record and 'תאריך' in current_record and 'מספרים' in current_record:
                    records.append(current_record)
                current_record = {'תאריך': lines[i+1] if i+1 < len(lines) else "", 'זכיות_ערך': 0.0}
                i += 1
            elif "המספר החזק:" in line:
                try: current_record['חזק'] = int(lines[i+1])
                except: pass
                i += 1
            elif "המספרים שעלו בגורל:" in line or "מספרים:" in line:
                start = i + 1
                if start < len(lines) and lines[start] == "": start += 1
                nums = []
                for j in range(6):
                    if start + j < len(lines):
                        try: nums.append(int(lines[start+j]))
                        except: pass
                current_record['מספרים'] = nums
                i = start + 5
            else:
                # מנגנון חילוץ סכומים חכם: מחפש מספרים גדולים בשורות שקשורות לכסף או פרסים
                keywords = ["זכיות", "פרס", "₪", "סכום", "שקל", "חלוקה", "תוצאות"]
                if any(kw in line for kw in keywords):
                    # מוצא את כל המספרים בשורה כולל כאלה עם פסיקים
                    numbers_found = re.findall(r'\b\d{1,3}(?:,\d{3})*(?:\.\d+)?\b|\b\d+\b', line)
                    for num_str in numbers_found:
                        try:
                            clean_num = float(num_str.replace(',', ''))
                            # אנחנו מחפשים את סכומי הפרסים הגדולים (למשל מעל 10,000 ש"ח) כדי לא לבלבל עם תאריכים או כמויות זוכים קטנות
                            if clean_num > 10000 and clean_num > current_record.get('זכיות_ערך', 0):
                                current_record['זכיות_ערך'] = clean_num
                        except:
                            pass
            i += 1
        if current_record and 'תאריך' in current_record and 'מספרים' in current_record:
            records.append(current_record)
        return records, lines[:30] # מחזיר גם את 30 השורות הראשונות לבדיקה
    except Exception as e:
        return None, [str(e)]

# טעינת הנתונים
records, raw_lines_preview = parse_lotto_file('lotto2026.csv')

if records:
    records.reverse()
    
    all_numbers = []
    for r in records:
        if 'מספרים' in r:
            all_numbers.extend(r['מספרים'])
            
    counts = Counter(all_numbers)
    top_20_pool = [n for n, c in counts.most_common(20)]
    
    st.title("🎰 מחולל לוטו אסטרטגי")
    
    # --- תצוגת בדיקה טכנית למקרה של סכום 0 ---
    all_values = [r['זכיות_ערך'] for r in records if r.get('זכיות_ערך', 0) > 0]
    
    if not all_values:
        st.sidebar.warning("🛠️ בדיקת מבנה הקובץ:")
        st.sidebar.write("הקוד לא מצא סכומים כספיים ברורות. הנה הצצה לאיך שהקובץ שלך בנוי בפנים:")
        st.sidebar.code("\n".join(raw_lines_preview))
    
    st.subheader("💰 ניתוח פיננסי: מספרים חזקים וזכיות גדולות")
    
    global_average = sum(all_values) / len(all_values) if all_values else 0
    
    financial_data = []
    for strong_num in range(1, 8):
        matching_draws = [r for r in records if r.get('חזק') == strong_num]
        
        big_wins_count = sum(1 for r in matching_draws if r.get('זכיות_ערך', 0) >= global_average and global_average > 0)
        
        draw_values = [r['זכיות_ערך'] for r in matching_draws if r.get('זכיות_ערך', 0) > 0]
        avg_win_amount = sum(draw_values) / len(draw_values) if draw_values else 0
        
        financial_data.append({
            "מספר חזק": f"מספר {strong_num}",
            "כמות זכיות גדולות השנה": f"{big_wins_count} זכיות" if global_average > 0 else "אין נתונים",
            "סכום זכייה ממוצע": f"₪ {avg_win_amount:,.0f}" if avg_win_amount > 0 else "לא זוהה סכום בקובץ",
            "סדר_מיון": avg_win_amount
        })
        
    financial_df = pd.DataFrame(financial_data).sort_values(by="סדר_מיון", ascending=False).drop(columns=["סדר_מיון"])
    st.dataframe(financial_df.set_index("מספר חזק"), use_container_width=True)
    
    st.divider()
    
    st.subheader("🔮 בדיקת סיכוי למספר החזק הבא")
    chosen_strong = st.selectbox("בחר את המספר החזק שיצא בהגרלה האחרונה:", options=list(range(1, 8)), index=5)
    
    next_strong_list = []
    for i in range(len(records) - 1):
        if records[i].get('חזק') == chosen_strong:
            next_draw = records[i+1]
            if next_draw.get('חजק'):
                next_strong_list.append(next_draw['חזק'])
                
    total_cases = len(next_strong_list)
    counts_after_chosen = Counter(next_strong_list)
    
    if total_cases > 0:
        stats_data = []
        for i in range(1, 8):
            times = counts_after_chosen.get(i, 0)
            chance = (times / total_cases) * 100
            stats_data.append({
                "המספר החזק הבא": f"מספר {i}",
                "כמה פעמים יצא אחריו השנה": f"{times} פעמים",
                "אחוז סיכוי": f"{chance:.1f}%",
                "סיכוי_עזר": chance
            })
        stats_df = pd.DataFrame(stats_data).sort_values(by="סיכוי_עזר", ascending=False).drop(columns=["סיכוי_עזר"])
        st.dataframe(stats_df.set_index("המספר החזק הבא"), use_container_width=True)
        
    st.divider()
    st.write("בחר את שיטת הגרלת 8 הטבלאות המועדפת עליך:")
    
    selected_strong = random.
