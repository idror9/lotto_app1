import streamlit as st
import pandas as pd
from collections import Counter

st.set_page_config(page_title="ניתוח לוטו שנתי", page_icon="🎰", layout="wide")

st.title("🎰 ניתוח היסטוריית לוטו שנתית")
st.write("המערכת מנתחת את הקובץ שיצרת ומציגה נתונים מהשנה האחרונה")

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
                try:
                    current_record['חזק'] = int(lines[i+1])
                except:
                    pass
                i += 1
            elif "המספרים שעלו בגורל:" in line:
                start = i + 1
                if start < len(lines) and lines[start] == "":
                    start += 1
                nums = []
                for j in range(6):
                    if start + j < len(lines):
                        try:
                            nums.append(int(lines[start+j]))
                        except:
                            pass
                current_record['מספרים'] = nums
                i = start + 5
            elif "סך הכל זכיות בהגרלה:" in line:
                if 'תאריך' in current_record and 'מספרים' in current_record:
                    records.append(current_record)
                current_record = {}
            i += 1
        return pd.DataFrame(records)
    except Exception as e:
        st.error(f"שגיאה בקריאת הקובץ: {e}")
        return None

# טעינת הנתונים מהקובץ שהעלית
df = parse_lotto_file('lotto2026.csv')

if df is not None and not df.empty:
    st.sidebar.success(f"זוהו {len(df)} הגרלות מהשנה האחרונה")
    
    # תצוגת טבלה
    st.subheader("📜 היסטוריית הגרלות")
    display_df = df.copy()
    display_df['מספרים'] = display_df['מספרים'].apply(lambda x: ", ".join(map(str, x)))
    st.dataframe(display_df, use_container_width=True)
    
    # חישוב סטטיסטיקה
    all_numbers = []
    all_strong = []
    for index, row in df.iterrows():
        all_numbers.extend(row['מספרים'])
        if 'חזק' in row:
            all_strong.append(row['חזק'])
            
    counts = Counter(all_numbers)
    hot_10 = [n for n, c in counts.most_common(10)]
    hot_10.sort()
    
    strong_counts = Counter(all_strong)
    hot_strong = strong_counts.most_common(1)[0][0] if all_strong else "לא ידוע"

    st.divider()
    
    # הצגת תוצאות הניתוח
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🔥 10 המספרים החמים")
        st.write(", ".join(map(str, hot_10)))
    with col2:
        st.subheader("🎯 המספר החזק הכי נפוץ")
        st.metric("חזק מומלץ", hot_strong)

    # טבלאות צמצום
    st.subheader("📋 טבלאות צמצום מוצעות")
    h = hot_10
    if len(h) >= 10:
        t1 = [h[0], h[1], h[2], h[3], h[4], h[5]]
        t2 = [h[4], h[5], h[6], h[7], h[8], h[9]]
        t3 = [h[0], h[2], h[4], h[6], h[8], h[9]]
        
        st.info(f"טבלה 1: {sorted(t1)} + חזק {hot_strong}")
        st.info(f"טבלה 2: {sorted(t2)} + חזק {hot_strong}")
        st.info(f"טבלה 3: {sorted(t3)} + חזק {hot_strong}")
else:
    st.warning("לא הצלחתי למצוא נתונים בקובץ. וודא ששם הקובץ בגיטהאב הוא בדיוק lotto2026.csv")
