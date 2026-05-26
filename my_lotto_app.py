import streamlit as st
import pandas as pd
from collections import Counter
import random
import re

# הגדרת דף נקייה והסתרת תפריטים מיותרים לנייד
st.set_page_config(page_title="לוטו חכם - אבחון קובץ", layout="centered")

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stButton>button {width: 100%; border-radius: 20px; height: 3.5em; font-weight: bold; margin-bottom: 10px;}
    </style>
    """, unsafe_allow_html=True)

# קריאת הקובץ בצורה הגולמית ביותר לצורך בדיקה
raw_content_preview = ""
try:
    with open('lotto2026.csv', 'r', encoding='utf8') as f:
        raw_lines = f.readlines()
        raw_content_preview = "".join(raw_lines[:25]) # לקיחת 25 השורות הראשונות
except Exception as e:
    raw_content_preview = f"שגיאה בקריאת הקובץ: {e}"

st.title("🎰 לוטו חכם: מערכת אנליזה")

# הצגת תוכן הקובץ הגולמי כדי שנבין מה קורה בפנים
st.subheader("🛠️ בדיקת מבנה הקובץ הגולמי (דיאגנוסטיקה)")
st.write("כך הקובץ שלך נראה בפנים במציאות. תראה לי מה כתוב כאן כדי שנתקן את הניתוח:")
st.code(raw_content_preview)

st.divider()

# פונקציית חילוץ בסיסית שמנסה לקרוא שורות קבועות
def parse_lotto_file_diagnostic(file_path):
    try:
        with open(file_path, 'r', encoding='utf8') as f:
            lines = [line.strip() for line in f.readlines()]
        records = []
        current_record = {}
        i = 0
        while i < len(lines):
            line = lines[i]
            if "תאריך" in line:
                if current_record and 'מספרים' in current_record:
                    records.append(current_record)
                current_record = {'פרס_גדול': False, 'חזק': None}
            elif "חזק" in line:
                nums = re.findall(r'\b[1-7]\b', line)
                if nums: current_record['חזק'] = int(nums[0])
                elif i+1 < len(lines) and lines[i+1].strip().isdigit():
                    current_record['חזק'] = int(lines[i+1].strip())
            elif "מספרים" in line or "גורל" in line:
                start = i + 1
                if start < len(lines) and lines[start] == "": start += 1
                nums = []
                for j in range(6):
                    if start + j < len(lines) and lines[start+j].strip().isdigit():
                        nums.append(int(lines[start+j].strip()))
                if len(nums) == 6: current_record['מספרים'] = nums
            if "זכיות" in line or "פרס" in line:
                current_record['פרס_גדול'] = True
            i += 1
        if current_record and 'מספרים' in current_record:
            records.append(current_record)
        return records
    except:
        return None

records_year = parse_lotto_file_diagnostic('lotto2026.csv')

if records_year:
    # לקיחת 104 הגרלות (שנה אחורה) וסידור כרונולוגי
    records_year = records_year[:104]
    records_year.reverse()
    
    all_numbers = []
    all_strong = []
    for r in records_year:
        if 'מספרים' in r: all_numbers.extend(r['מספרים'])
        if r.get('חזק'): all_strong.append(r['חזק'])
            
    counts = Counter(all_numbers)
    strong_counts = Counter(all_strong)
    
    top_20_pool = [n for n, c in counts.most_common(20)]
    cold_numbers = [n for n in range(1, 38) if n not in top_20_pool][:7]
    
    # === חלק 1: ניתוח פיננסי ===
    st.subheader("💰 ניתוח פיננסי: מספרים חזקים ופוטנציאל הפרס")
    
    financial_data = []
    for strong_num in range(1, 8):
        matching_draws = [r for r in records_year if r.get('חזק') == strong_num]
        total_draws_for_num = len(matching_draws)
        big_wins = sum(1 for r in matching_draws if r.get('פרס_גדול', False))
        
        raw_power = (big_wins / total_draws_for_num * 100) if total_draws_for_num > 0 else 0
        final_power = (raw_power * 0.7) + ((strong_counts.get(strong_num, 0) / len(records_year) * 100) * 0.3) if records_year else 0
        
        financial_data.append({
            "מספר חזק": f"מספר {strong_num}",
            "הופעות בשנה האחרונה": f"{total_draws_for_num} פעמים",
            "מדד עוצמה כספית": f"{final_power:.1f}%",
            "סדר_מיון": final_power
        })
        
    financial_df = pd.DataFrame(financial_data).sort_values(by="סדר_מיון", ascending=False).drop(columns=["סדר_מיון"])
    st.dataframe(financial_df.set_index("מספר חזק"), use_container_width=True)
    
    st.divider()
    
    # === חלק 2: לוח תחזיות מבוסס 5 הסעיפים ===
    st.header("🔮 תמונת המצב והתחזית הטכנולוגית")
    
    with st.expander("📊 סעיף 1: ניתוח סטטיסטי"):
        st.write(f"**המספרים החמים ביותר:** {', '.join(map(str, top_20_pool[:6]))}")
        st.write(f"**המספרים הקרים ביותר:** {', '.join(map(str, cold_numbers))}")
    
    # === חלק 3: בדיקת סיכוי למספר החזק הבא ===
    st.subheader("🔮 בדיקת סיכוי למספר החזק הבא")
    chosen_strong = st.selectbox("בחר את המספר החזק שיצא בהגרלה האחרונה:", options=list(range(1, 8)), index=5)
    
    next_strong_list = []
    for i in range(len(records_year) - 1):
        if records_year[i].get('חזק') == chosen_strong:
            next_draw = records_year[i+1]
            if next_draw.get('חזק'): next_strong_list.append(next_draw['חזק'])
                
    total_cases = len(next_strong_list)
    counts_after_chosen = Counter(next_strong_list)
    
    st.write(f"המספר **{chosen_strong}** יצא {total_cases} פעמים בחלון הזמן של השנה האחרונה.")
    
    if total_cases > 0:
        stats_data = []
        for i in range(1, 8):
            times = counts_after_chosen.get(i, 0)
            chance = (times / total_cases) * 100
            stats_data.append({
                "המספר החזק הבא": f"מספר {i}",
                "כמה פעמים יצא אחריו בשנה זו": f"{times} פעמים",
                "אחוז סיכוי": f"{chance:.1f}%",
                "סיכוי_עזר": chance
            })
        stats_df = pd.DataFrame(stats_data).sort_values(by="סיכוי_עזר", ascending=False).drop(columns=["סיכוי_עזר"])
        st.dataframe(stats_df.set_index("המספר החזק הבא"), use_container_width=True)
        
    st.divider()
    st.write("### הפקת טורים חכמים למילוי:")
    
    selected_strong = random.randint(1, 7)

    if st.button("🎲 כפתור 1: הגרלה דינמית רגילה"):
        current_hot_12 = random.sample(top_20_pool, 12)
        st.write(f"**נבחר מספר חזק אחיד:** {selected_strong}")
        for i in range(1, 9):
            nums = sorted(random.sample(current_hot_12, 6))
            st.info(f"טבלה {i}: {', '.join(map(str, nums))} | חזק: {selected_strong}")
            
    if st.button("📈 כפתור 2: הגרלת סדרות ומרווחים"):
        current_hot_12 = random.sample(top_20_pool, 12)
        st.write(f"**נבחר מספר חזק אחיד:** {selected_strong}")
        for i in range(1, 9):
            table = sorted(random.sample(current_hot_12, 6))
            st.success(f"טבלה {i}: {', '.join(map(str, table))} | חזק: {selected_strong}")
else:
    st.warning("המערכת לא הצליחה לחלץ הגרלות במבנה הנוכחי, אך תוכן הקובץ מוצג למעלה בבלוק השחור.")
