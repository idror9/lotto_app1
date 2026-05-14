import streamlit as st
import pandas as pd
from collections import Counter
import random

st.set_page_config(page_title="מנחש הלוטו החכם", page_icon="🎰", layout="wide")

st.title("🎰 מחולל הגרלות: 12 חמים וחזק מכל הטווח")
st.write("בכל לחיצה יוגרלו 8 טבלאות עם מספר חזק אחד שנבחר מתוך כל 7 האפשרויות")

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
    
    strong_counts = Counter(all_strong)

    st.subheader("🔥 נתוני השנה האחרונה")
    c1, c2 = st.columns(2)
    with c1:
        st.write("**12 המספרים הרגילים החמים (לפי שכיחות):**")
        st.write(", ".join(map(str, sorted(hot_12))))
    with c2:
        # הצגת הגרף כדי לראות את כל 7 המספרים החזקים
        strong_data = pd.DataFrame([{'מספר חזק': str(i), 'פעמים': strong_counts.get(i, 0)} for i in range(1, 8)])
        st.bar_chart(strong_data.set_index('מספר חזק'))

    st.divider()

    if st.button("🎲 הגרל 8 טבלאות (חזק אחיד מתוך 1-7)"):
        # בחירת מספר חזק אחד אקראי מתוך כל 7 האפשרויות
        selected_strong = random.randint(1, 7)
        
        st.subheader(f"📋 תוצאות ההגרלה (מספר חזק שנבחר הפעם: {selected_strong})")
        
        for i in range(0, 8, 2):
            col1, col2 = st.columns(2)
            
            with col1:
                t1_nums = sorted(random.sample(hot_12, 6))
                st.success(f"**טבלה {i+1}:** {t1_nums} | **חזק:** {selected_strong}")
            
            with col2:
                t2_nums = sorted(random.sample(hot_12, 6))
                st.success(f"**טבלה {i+2}:** {t2_nums} | **חזק:** {selected_strong}")
        
        st.balloons()
    else:
        st.info("לחץ על הכפתור כדי לייצר שילובים חדשים. המערכת תבחר באקראי מספר חזק אחד מתוך הטווח המלא (1-7).")

else:
    st.error("לא נמצא קובץ נתונים.")
