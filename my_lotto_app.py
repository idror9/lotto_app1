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
    # הפיכת הרשימה לסדר כרונולוגי
    records.reverse()
    
    # חילוץ נתונים כלליים למאגר המספרים החמים
    all_numbers = []
    for r in records:
        if 'מספרים' in r:
            all_numbers.extend(r['מספרים'])
            
    counts = Counter(all_numbers)
    top_20_pool = [n for n, c in counts.most_common(20)]
    
    st.title("🎰 מחולל לוטו אסטרטגי")
    
    st.subheader("💰 ניתוח פיננסי: מספרים חזקים וזכיות גדולות")
    
    # חישוב רף ממוצע לזכייה גדולה מתוך כל הקובץ
    all_values = [r['זכיות_ערך'] for r in records if 'זכיות_ערך' in r and r['זכיות_ערך'] > 0]
    global_average = sum(all_values) / len(all_values) if all_values else 0
    
    # בניית הסטטיסטיקה הפיננסית לכל מספר חזק (1 עד 7)
    financial_data = []
    for strong_num in range(1, 8):
        # סינון ההגרלות שבהן עלה המספר החזק הנוכחי
        matching_draws = [r for r in records if r.get('חזק') == strong_num]
        
        # ספירת כמה מתוכן עברו את רף הזכייה הגדולה
        big_wins_count = sum(1 for r in matching_draws if r.get('זכיות_ערך', 0) >= global_average)
        
        # חישוב סכום הזכייה הממוצע הספציפי למספר החזק הזה
        draw_values = [r['זכיות_ערך'] for r in matching_draws if 'זכיות_ערך' in r and r['זכיות_ערך'] > 0]
        avg_win_amount = sum(draw_values) / len(draw_values) if draw_values else 0
        
        financial_data.append({
            "מספר חזק": f"מספר {strong_num}",
            "כמות זכיות גדולות השנה": f"{big_wins_count} זכיות",
            "סכום זכייה ממוצע": f"₪ {avg_win_amount:,.0f}",
            "סדר_מיון": avg_win_amount
        })
        
    # מיון הטבלה מהסכום הממוצע הגבוה ביותר לנמוך ביותר
    financial_df = pd.DataFrame(financial_data).sort_values(by="סדר_מיון", ascending=False)
    financial_df = financial_df.drop(columns=["סדר_מיון"])
    
    st.write("הטבלה מסודרת מהמספר שהביא את הפרס הממוצע הגבוה ביותר להכי נמוך:")
    st.dataframe(financial_df.set_index("מספר חזק"), use_container_width=True)
    
    st.divider()
    
    # --- חלק 2: בדיקת סיכוי למספר החזק הבא (התכונה מהשלב הקודם) ---
    st.subheader("🔮 בדיקת סיכוי למספר החזק הבא")
    chosen_strong = st.selectbox("בחר את המספר החזק שיצא בהגרלה האחרונה:", options=list(range(1, 8)), index=5)
    
    next_strong_list = []
    for i in range(len(records) - 1):
        if records[i].get('חזק') == chosen_strong:
            next_draw = records[i+1]
            if next_draw.get('חזק'):
                next_strong_list.append(next_draw['חזק'])
                
    total_cases = len(next_strong_list)
    counts_after_chosen = Counter(next_strong_list)
    
    if total_cases > 0:
        stats_data = []
        for i in range(1, 8):
            times = counts_after_chosen.get(i, 0)
            chance = (times / total_cases) * 100
            stats_data.append({
                "המספר החזק הבא": f"מספר {i}",
                "כמה פעמים יצא אחריו השנה": f"{times} פעמים",
                "אחוז סיכוי": f"{chance:.1f}%",
                "סיכוי_עזר": chance
            })
        stats_df = pd.DataFrame(stats_data).sort_values(by="סיכוי_עזר", ascending=False).drop(columns=["סיכוי_עזר"])
        st.dataframe(stats_df.set_index("המספר החזק הבא"), use_container_width=True)
        
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
