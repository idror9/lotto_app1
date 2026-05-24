import streamlit as st
import pandas as pd
from collections import Counter
import random

st.set_page_config(page_title="לוטו חכם", page_icon="🎰", layout="centered")

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
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f.readlines()]
        records = []
        current_record = {}
        i = 0
        while i < len(lines):
            line = lines[i]
            if "תאריך הגרלה:" in line:
                current_record['תאריך'] = lines[i+1]
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
                if 'תאריך' in current_record and 'מספרים' in current_record:
                    records.append(current_record)
                current_record = {}
            i += 1
        return pd.DataFrame(records)
    except Exception as e:
        return None

df = parse_lotto_file('lotto2026.csv')

if df is not None and not df.empty:
    all_numbers = []
    all_strong = []
    for _, row in df.iterrows():
        all_numbers.extend(row['מספרים'])
        if 'חזק' in row: all_strong.append(row['חזק'])
            
    counts = Counter(all_numbers)
    top_20_pool = [n for n, c in counts.most_common(20)]

    st.title("🎰 מחולל לוטו אסטרטגי")
    st.write("בחר את שיטת הגרלת 8 הטבלאות המועדפת עליך:")
    
    selected_strong = random.randint(1, 7)

    # כפתור 1: הגרלה רגילה מהחמים
    if st.button("🎲 כפתור 1: הגרלה דינמית רגילה (מתוך 20 החמים)"):
        current_hot_12 = random.sample(top_20_pool, 12)
        st.subheader(f"נבחר מספר חזק: {selected_strong}")
        st.write(f"**12 המספרים שנבחרו:** {', '.join(map(str, sorted(current_hot_12)))}")
        
        for i in range(1, 9):
            nums = sorted(random.sample(current_hot_12, 6))
            st.info(f"**טבלה {i}:** \n\n {', '.join(map(str, nums))}  |  **חזק:** {selected_strong}")
        st.balloons()

    # כפתור 2: הגרלה מבוססת מרווחים וסדרות
    if st.button("📈 כפתור 2: הגרלת סדרות ומרווחים (הפרשים קרובים 1, 2, 3)"):
        # בחירת 12 מספרים מהמאגר שיש ביניהם קרבה
        current_hot_12 = random.sample(top_20_pool, 12)
        st.subheader(f"נבחר מספר חזק: {selected_strong}")
        st.write(f"**12 המספרים שנבחרו לאסטרטגיית מרווחים:** {', '.join(map(str, sorted(current_hot_12)))}")
        
        for i in range(1, 9):
            # לוגיקה שמייצרת טבלה עם עדיפות להפרשים קטנים (1, 2, 3) כפי שקורה בהגרלות האמיתיות
            valid_table = False
            attempts = 0
            while not valid_table and attempts < 100:
                table = random.sample(current_hot_12, 6)
                table.sort()
                diffs = [table[j+1] - table[j] for j in range(5)]
                # בדיקה אם יש לפחות הפרש אחד של 1 או 2 או 3 (הכי נפוצים בשנה האחרונה)
                if any(d in [1, 2, 3] for d in diffs):
                    valid_table = True
                attempts += 1
            
            st.success(f"**טבלה {i} (מבוססת מרווחים):** \n\n {', '.join(map(str, table))}  |  **חזק:** {selected_strong}")
        st.balloons()

else:
    st.error("קובץ הנתונים לא נמצא")
