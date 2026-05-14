import streamlit as st
import pandas as pd
from collections import Counter

st.set_page_config(page_title="מנחש הלוטו החכם", page_icon="🎰", layout="wide")

st.title("🎰 ניתוח לוטו: 12 חמים ו-8 טבלאות צמצום")
st.write("התאמה למילוי טפסים זוגיים (8 טבלאות)")

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
    hot_12.sort()
    
    strong_counts = Counter(all_strong)
    strong_data = pd.DataFrame([
        {'מספר חזק': str(i), 'פעמים שהופיע': strong_counts.get(i, 0)} 
        for i in range(1, 8)
    ])
    hot_strong = strong_counts.most_common(1)[0][0] if all_strong else "N/A"

    col_a, col_b = st.columns([1, 1])
    with col_a:
        st.subheader("📊 התפלגות מספרים חזקים")
        st.bar_chart(strong_data.set_index('מספר חזק'))
    with col_b:
        st.subheader("🔥 12 המספרים החמים")
        st.write(", ".join(map(str, hot_12)))
        st.info(f"המספר החזק הנפוץ ביותר: **{hot_strong}**")

    st.divider()
    st.subheader("📋 8 טבלאות צמצום למילוי")
    st.write("הטבלאות מסודרות בזוגות כדי להקל על מילוי הטופס:")

    h = hot_12
    if len(h) >= 12:
        # יצירת 8 קומבינציות לכיסוי אופטימלי של 12 מספרים
        combinations = [
            [h[0], h[1], h[2], h[3], h[4], h[5]],   # טבלה 1
            [h[6], h[7], h[8], h[9], h[10], h[11]], # טבלה 2
            [h[0], h[1], h[2], h[6], h[7], h[8]],   # טבלה 3
            [h[3], h[4], h[5], h[9], h[10], h[11]], # טבלה 4
            [h[0], h[3], h[6], h[9], h[2], h[11]],  # טבלה 5
            [h[1], h[4], h[7], h[10], h[5], h[8]],  # טבלה 6
            [h[0], h[2], h[4], h[6], h[8], h[10]],  # טבלה 7
            [h[1], h[3], h[5], h[7], h[9], h[11]]   # טבלה 8 (משלימה)
        ]
        
        # תצוגה בזוגות (כמו בטופס)
        for i in range(0, 8, 2):
            c1, c2 = st.columns(2)
            with c1:
                st.success(f"**טבלה {i+1}:** {sorted(combinations[i])} | **חזק:** {hot_strong}")
            with c2:
                st.success(f"**טבלה {i+2}:** {sorted(combinations[i+1])} | **חזק:** {hot_strong}")
    
    st.divider()
    st.subheader("📜 ארכיון הגרלות")
    st.dataframe(df, use_container_width=True)
else:
    st.error("לא נמצא קובץ נתונים.")
