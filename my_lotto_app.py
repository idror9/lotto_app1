import streamlit as st
import pandas as pd
from collections import Counter
import random

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
            if "תאריך הגרלה:" in line:
                if current_record and 'תאריך' in current_record and 'מספרים' in current_record:
                    records.append(current_record)
                current_record = {'תאריך': lines[i+1]}
                i += 1
            elif "המספר החזק:" in line:
                try: current_record['חזק'] = int(lines[i+1])
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
            elif "סך הכל זכיות בהגרלה:" in line:
                try:
                    # ניסיון לחלץ את סכום הזכיות או כמות הזוכים כמדד לזכייה גדולה
                    clean_val = lines[i+1].replace(',', '').replace('₪', '').strip()
                    current_record['זכיות_ערך'] = float(clean_val)
                except:
                    current_record['זכיות_ערך'] = 0
                i += 1
            i += 1
        if current_record and 'תאריך' in current_record and 'מספרים' in current_record:
            records.append(current_record)
        return records
    except:
        return None

# טעינת הנתונים
records = parse_lotto_file('lotto2026.csv')

if records:
    # הפיכת הרשימה לסדר כרונולוגי (מהישן לחדש)
    records.reverse()
    
    # חילוץ נתונים כלליים
    all_numbers = []
    for r in records:
        if 'מספרים' in r:
            all_numbers.extend(r['מספרים'])
            
    counts = Counter(all_numbers)
    top_20_pool = [n for n, c in counts.most_common(20)]
    
    # חישוב רף ל"זכייה גדולה" (לפי חציון הזכיות בקובץ)
    all_values = [r['זכיות_ערך'] for r in records if 'זכיות_ערך' in r and r['זכיות_ערך'] > 0]
    threshold = sum(all_values) / len(all_values) if all_values else 0
    
    next_strong_all = []
    next_strong_big_win = []
    
    for i in range(len(records) - 1):
        if records[i].get('חזק') == 2:
            next_draw = records[i+1]
            if next_draw.get('חזק'):
                next_strong_all.append(next_draw['חזק'])
                # אם בהגרלה של ה-2 הייתה זכייה גדולה מהממוצע
                if records[i].get('זכיות_ערך', 0) >= threshold:
                    next_strong_big_win.append(next_draw['חזק'])
                    
    st.title("🎰 מחולל לוטו אסטרטגי")
    
    # טבלה 1: שכיחות כללית אחרי 2
    st.subheader("📊 שכיחות כללית: מה עלה מיד אחרי מספר 2")
    total_cases = len(next_strong_all)
    if total_cases > 0:
        stats_all = []
        for i in range(1, 8):
            times = next_strong_all.count(i)
            chance = (times / total_cases) * 100
            stats_all.append({"מספר חזק עוקב": i, "כמות הופעות": times, "סיכוי": f"{chance:.1f}%"})
        st.dataframe(pd.DataFrame(stats_all).set_index("מספר חזק עוקב"), use_container_width=True)
        
    # טבלה 2: שכיחות ממוקדת בזכיות גדולות
    st.subheader("💰 שכיחות מיוחדת: מה עלה אחרי מספר 2 שהביא זכייה גדולה")
    total_big_cases = len(next_strong_big_win)
    st.write(f"מתוך מופעי ה-2, נמצאו {total_big_cases} הגרלות עם היקף זכיות גבוה מהרגיל.")
    
    if total_big_cases > 0:
        stats_big = []
        for i in range(1, 8):
            times = next_strong_big_win.count(i)
            chance = (times / total_big_cases) * 100
            stats_big.append({"מספר חזק עוקב": i, "כמות הופעות": times, "סיכוי": f"{chance:.1f}%"})
        st.dataframe(pd.DataFrame(stats_big).set_index("מספר חזק עוקב"), use_container_width=True)
    else:
        st.info("אין מספיק נתוני זכיות בקובץ כדי לפלח זכיות גדולות.")
        
    st.divider()
    st.write("בחר את שיטת הגרלת 8 הטבלאות המועדפת עליך:")
    
    selected_strong = random.randint(1, 7)

    # כפתור 1
    if st.button("🎲 כפתור 1: הגרלה דינמית רגילה (מתוך 20 החמים)"):
        current_hot_12 = random.sample(top_20_pool, 12)
        st.subheader(f"נבחר מספר חזק אחיד: {selected_strong}")
        st.write(f"12 המספרים שנבחרו להגרלה זו: {', '.join(map(str, sorted(current_hot_12)))}")
        for i in range(1, 9):
            nums = sorted(random.sample(current_hot_12, 6))
            st.info(f"טבלה {i}: \n\n {', '.join(map(str, nums))}  |  חזק: {selected_strong}")
        st.balloons()

    # כפתור 2
    if st.button("📈 כפתור 2: הגרלת סדרות ומרווחים (הפרשים קרובים)"):
        current_hot_12 = random.sample(top_20_pool, 12)
        st.subheader(f"נבחר מספר חזק אחיד: {selected_strong}")
        st.write(f"12 המספרים שנבחרו לאסטרטגיית מרווחים: {', '.join(map(str, sorted(current_hot_12)))}")
        for i in range(1, 9):
            valid_table = False
            attempts = 0
            while not valid_table and attempts < 100:
                table = random.sample(current_hot_12, 6)
                table.sort()
                diffs = [table[j+1] - table[j] for j in range(5)]
                if any(d in [1, 2, 3] for d in diffs):
                    valid_table = True
                attempts += 1
            st.success(f"טבלה {i} (מבוססת מרווחים): \n\n {', '.join(map(str, table))}  |  חזק: {selected_strong}")
        st.balloons()
else:
    st.error("קובץ הנתונים 'lotto2026.csv' לא נמצא.")
