import streamlit as st
import pandas as pd
from collections import Counter
import random

st.set_page_config(page_title="מנחש הלוטו החכם", page_icon="🎰", layout="wide")

st.title("🎰 ניתוח לוטו: 12 חמים עם מחולל הגרלות")
st.write("לחץ על הכפתור למטה כדי לייצר שילובים חדשים מתוך 12 המספרים החמים")

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
    hot_strong = strong_counts.most_common(1)[0][0] if all_strong else "N/A"

    # הצגת נתונים בסיסיים
    st.subheader("🔥 12 המספרים החמים שזוהו")
    st.write(", ".join(map(str, sorted(hot_12))))
    st.info(f"המספר החזק הנפוץ ביותר: **{hot_strong}**")

    st.divider()

    # כפתור הגרלה
    if st.button("🎲 הגרל 8 טבלאות חדשות מהמספרים החמים"):
        st.subheader("📋 8 טבלאות שהוגרלו עבורך (מתוך ה-12)")
        
        generated_tables = []
        for _ in range(8):
            # בחירת 6 מספרים אקראיים מתוך ה-12 החמים
            table = random.sample(hot_12, 6)
            generated_tables.append(sorted(table))
        
        # תצוגה בזוגות
        for i in range(0, 8, 2):
            c1, c2 = st.columns(2)
            with c1:
                st.success(f"**טבלה {i+1}:** {generated_tables[i]} | **חזק:** {hot_strong}")
            with c2:
                st.success(f"**טבלה {i+2}:** {generated_tables[i+1]} | **חזק:** {hot_strong}")
        
        st.balloons() # אפקט חגיגי
    else:
        st.info("לחץ על הכפתור למעלה כדי לייצר את הטבלאות למילוי.")

    st.divider()
    # גרף מספרים חזקים
    strong_data = pd.DataFrame([{'מספר חזק': str(i), 'פעמים': strong_counts.get(i, 0)} for i in range(1, 8)])
    st.subheader("📊 התפלגות המספר החזק")
    st.bar_chart(strong_data.set_index('מספר חזק'))

else:
    st.error("לא נמצא קובץ נתונים.")
