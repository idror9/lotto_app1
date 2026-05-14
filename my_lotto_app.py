import streamlit as st
import pandas as pd
from collections import Counter
import random

st.set_page_config(page_title="מנחש הלוטו החכם", page_icon="🎰", layout="wide")

st.title("🎰 מחולל הגרלות: 12 חמים וחזק משתנה")
st.write("בכל לחיצה יוגרלו 8 טבלאות עם מספרים חזקים שונים מהמובילים")

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
        st.error(f"שגיאה: {e}")
        return None

df = parse_lotto_file('lotto2026.csv')

if df is not None and not df.empty:
    all_numbers = []
    all_strong = []
    for _, row in df.iterrows():
        all_numbers.extend(row['מספרים'])
        if 'חזק' in row: all_strong.append(row['חזק'])
            
    counts = Counter(all_numbers)
    hot_12 = [n for n, c in counts.most_common(12)]
    
    # זיהוי 3 המספרים החזקים הכי נפוצים
    strong_counts = Counter(all_strong)
    top_3_strong = [n for n, c in strong_counts.most_common(3)]

    st.subheader("🔥 נתוני השנה האחרונה")
    c1, c2 = st.columns(2)
    with c1:
        st.write("**12 המספרים הרגילים החמים:**")
        st.write(", ".join(map(str, sorted(hot_12))))
    with c2:
        st.write("**3 המספרים החזקים המובילים:**")
        st.write(", ".join(map(str, top_3_strong)))

    st.divider()

    if st.button("🎲 הגרל 8 טבלאות (מספרים וחזק משתנים)"):
        st.subheader("📋 תוצאות ההגרלה למילוי")
        
        # יצירת 8 טבלאות עם מספרים וחזק מוגרלים
        for i in range(0, 8, 2):
            col1, col2 = st.columns(2)
            
            # טבלה ראשונה בזוג
            t1_nums = sorted(random.sample(hot_12, 6))
            t1_strong = random.choice(top_3_strong)
            with col1:
                st.success(f"**טבלה {i+1}:** {t1_nums} | **חזק:** {t1_strong}")
            
            # טבלה שנייה בזוג
            t2_nums = sorted(random.sample(hot_12, 6))
            t2_strong = random.choice(top_3_strong)
            with col2:
                st.success(f"**טבלה {i+2}:** {t2_nums} | **חזק:** {t2_strong}")
        
        st.balloons()
    else:
        st.info("לחץ על הכפתור כדי לייצר שילובים חדשים.")

    st.divider()
    # תצוגת גרף חזקים לגיבוי
    strong_data = pd.DataFrame([{'מספר חזק': str(i), 'פעמים': strong_counts.get(i, 0)} for i in range(1, 8)])
    st.write("📊 גרף שכיחות מספר חזק:")
    st.bar_chart(strong_data.set_index('מספר חזק'))

else:
    st.error("לא נמצא קובץ נתונים.")
