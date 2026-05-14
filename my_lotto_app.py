import streamlit as st
import pandas as pd
from collections import Counter
import random

# הגדרת דף נקייה ללא תפריטים מיותרים
st.set_page_config(page_title="לוטו חכם", page_icon="🎰", layout="centered")

# עיצוב מותאם לנייד - הסתרת כפתורי מערכת של סטרימליט
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stButton>button {width: 100%; border-radius: 20px; height: 3em; font-weight: bold;}
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
    hot_12 = [n for n, c in counts.most_common(12)]
    
    strong_counts = Counter(all_strong)
    # כל 7 המספרים החזקים לבחירה
    all_possible_strong = list(range(1, 8))

    st.title("🎰 מחולל 8 טבלאות")
    st.write("מבוסס על 12 המספרים הכי חמים בשנה האחרונה")

    st.divider()

    if st.button("🎲 הגרל מספרים עכשיו"):
        # בחירת חזק אחיד מתוך כל ה-7
        selected_strong = random.randint(1, 7)
        
        st.subheader(f"נבחר מספר חזק: {selected_strong}")
        
        # הצגת הטבלאות בצורה ברורה מאוד לנייד
        for i in range(1, 9):
            nums = sorted(random.sample(hot_12, 6))
            # הצגת כל טבלה בתיבה נפרדת וגדולה
            st.info(f"**טבלה {i}:** \n\n {', '.join(map(str, nums))}  |  **חזק:** {selected_strong}")
        
        st.balloons()
    else:
        st.info("לחץ על הכפתור כדי לקבל את המספרים למילוי")

    # הסבר קצר בסוף, ללא גרפים
    with st.expander("לצפייה ב-12 המספרים החמים"):
        st.write(", ".join(map(str, sorted(hot_12))))

else:
    st.error("קובץ הנתונים לא נמצא")
