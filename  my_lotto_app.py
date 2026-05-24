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
            i += 1
        if current_record and 'תאריך' in current_record and 'מספרים' in current_record:
            records.append(current_record)
        return records
    except:
        return None

# טעינת הנתונים - ודא ששם הקובץ תואם בדיוק למה שיש בגיטהאב
records = parse_lotto_file('lotto2026.csv')

if records:
    # הפיכת הרשימה לסדר כרונולוגי מהישן לחדש כדי לנתח מה בא אחרי מה
    records.reverse()
    
    # חילוץ נתונים כלליים
    all_numbers = []
    all_strong = []
    for r in records:
        all_numbers.extend(r['מספרים'])
        if 'חזק' in r: 
            all_strong.append(r['חזק'])
            
    # יצירת מאגר 20 המספרים הרגילים הכי חמים
    counts = Counter(all_numbers)
    top_20_pool = [n for n, c in counts.most_common(20)]
    
    # ניתוח סטטיסטי: מה יוצא אחרי המספר החזק 2
    next_strong_after_2 = []
    for i in range(len(records) - 1):
        if records[i].get('חזק') == 2:
            next_draw = records[i+1]
            if next_draw.get('חזק'):
                next_strong_after_2.append(next_draw['חזק'])
                
    total_cases = len(next_strong_after_2)
    counts_after_2 = Counter(next_strong_after_2)
    
    st.title("🎰 מחולל לוטו אסטרטגי")
    
    # הצגת טבלת השכיחות של מה שיוצא אחרי 2
    st.subheader("📊 שכיחות: מספרים חזקים שעלו מיד אחרי המספר 2")
    st.write(f"המספר 2 הופיע כחזק {total_cases} פעמים לאורך ההיסטוריה בקובץ.")
    
    if total_cases > 0:
        stats_data = []
        for i in range(1, 8):
            times = counts_after_2.get(i, 0)
            chance = (times / total_cases) * 100
            stats_data.append({
                "מספר חזק עוקב": i,
                "כמות פעמים שהופיע": times,
                "הסתברות סטטיסטית": f"{chance:.1f}%"
            })
            
        stats_df = pd.DataFrame(stats_data)
        st.dataframe(stats_df.set_index("מספר חזק עוקב"), use_container_width=True)
    else:
        st.info("לא נמצאו מספיק נתונים על הופעת המספר 2 בקובץ.")
        
    st.divider()
    st.write("בחר את שיטת הגרלת 8 הטבלאות המועדפת עליך:")
    
    # הגרלת מספר חזק אחיד לסט הנוכחי (בין 1 ל-7)
    selected_strong = random.randint(1, 7)

    # כפתור 1: הגרלה רגילה מתוך ה-20 החמים
    if st.button("🎲 כפתור 1: הגרלה דינמית רגילה (מתוך 20 החמים)"):
        current_hot_12 = random.sample(top_20_pool, 12)
        st.subheader(f"נבחר מספר חזק אחיד: {selected_strong}")
        st.write(f"12 המספרים שנבחרו להגרלה זו: {', '.join(map(str, sorted(current_hot_12)))}")
        st.write("")
        
        for i in range(1, 9):
            nums = sorted(random.sample(current_hot_12, 6))
            st.info(f"טבלה {i}: \n\n {', '.join(map(str, nums))}  |  חזק: {selected_strong}")
        st.balloons()

    # כפתור 2: אסטרטגיית מרווחים (הפרשים קרובים של 1, 2 או 3)
    if st.button("📈 כפתור 2: הגרלת סדרות ומרווחים (הפרשים קרובים)"):
        current_hot_12 = random.sample(top_20_pool, 12)
        st.subheader(f"נבחר מספר חזק אחיד: {selected_strong}")
        st.write(f"12 המספרים שנבחרו לאסטרטגיית מרווחים: {', '.join(map(str, sorted(current_hot_12)))}")
        st.write("")
        
        for i in range(1, 9):
            valid_table = False
            attempts = 0
            while not valid_table and attempts < 100:
                table = random.sample(current_hot_12, 6)
                table.sort()
                # חישוב ההפרשים בין כל מספר עוקב בטבלה
                diffs = [table[j+1] - table[j] for j in range(5)]
                # אילוץ: לפחות אחד מההפרשים חייב להיות 1, 2 או 3 (הכי נפוצים במכונה)
                if any(d in [1, 2, 3] for d in diffs):
                    valid_table = True
                attempts += 1
            
            st.success(f"טבלה {i} (מבוססת מרווחים): \n\n {', '.join(map(str, table))}  |  חזק: {selected_strong}")
        st.balloons()

else:
    st.error("קובץ הנתונים לא נמצא. ודא ששם הקובץ בקוד (שורה 46) תואם בדיוק לשם הקובץ ב-GitHub.")
