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
    
    # ניקח מאגר רחב יותר של מספרים מובילים (למשל 20 המספרים הנפוצים ביותר בשנה האחרונה)
    top_numbers_pool = [n for n, c in counts.most_common(20)]

    st.title("🎰 מחולל 8 טבלאות דינמי")
    st.write("בכל לחיצה נבחרים 12 מספרים חמים שונים ומתוכם מורכבות הטבלאות")

    st.divider()

    if st.button("🎲 הגרל מספרים עכשיו"):
        # בכל לחיצה נבחרים 12 מספרים אקראיים מתוך מאגר ה-20 החמים
        current_hot_12 = random.sample(top_numbers_pool, 12)
        
        # בחירת חזק אחיד מתוך כל ה-7
        selected_strong = random.randint(1, 7)
        
        st.subheader(f"נבחר מספר חזק: {selected_strong}")
        
        # הצגת 12 המספרים שנבחרו להגרלה זו
        st.write(f"**12 המספרים שנבחרו להגרלה זו:** {', '.join(map(str, sorted(current_hot_12)))}")
        st.write("")
        
        # הגרלת 8 טבלאות מתוך ה-12 שנבחרו ברגע זה
        for i in range(1, 9):
            nums = sorted(random.sample(current_hot_12, 6))
            st.info(f"**טבלה {i}:** \n\n {', '.join(map(str, nums))}  |  **חזק:** {selected_strong}")
        
        st.balloons()
    else:
        st.info("לחץ על הכפתור כדי לקבל את המספרים למילוי")

else:
    st.error("קובץ הנתונים לא נמצא")
