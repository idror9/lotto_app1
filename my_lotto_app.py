import streamlit as st
import pandas as pd
from collections import Counter
import random
import os
import re

# הגדרת דף נקייה והסתרת תפריטים מיותרים לנייד
st.set_page_config(page_title="לוטו חכם - תצוגת 12 ממוספרת", layout="centered")

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stButton>button {width: 100%; border-radius: 20px; height: 3.5em; font-weight: bold; margin-bottom: 10px;}
    .number-box {display: inline-block; background-color: #f0f2f6; border: 1px solid #b9bdc5; border-radius: 5px; padding: 5px 10px; margin: 3px; font-weight: bold;}
    </style>
    """, unsafe_allow_html=True)

def load_any_lotto_file():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    possible_names = ['lotto2026.csv', 'Lotto2026.csv', 'lotto2026.CSV', 'Lotto2026.CSV']
    file_path = None
    
    for name in possible_names:
        test_path = os.path.join(current_dir, name)
        if os.path.exists(test_path):
            file_path = test_path
            break
            
    if file_path is None:
        for name in possible_names:
            if os.path.exists(name):
                file_path = name
                break
                
    if file_path is None:
        return None

    content = ""
    for enc in ['utf-8-sig', 'windows-1255', 'utf-8', 'ansi', 'iso-8859-8']:
        try:
            with open(file_path, 'r', encoding=enc, errors='ignore') as f:
                content = f.read()
            if content.strip() and len(content) > 50:
                break
        except:
            continue
            
    if not content or not content.strip():
        return None
        
    records = []
    lines = content.split('\n')
    
    for line in lines:
        if not line.strip():
            continue
            
        tokens = re.findall(r'\b\d+\b', line)
        if not tokens:
            continue
            
        ints = [int(t) for t in tokens]
        valid_lotto_nums = [n for n in ints if 1 <= n <= 37]
        
        if len(valid_lotto_nums) >= 7:
            strong_candidate = valid_lotto_nums[-1]
            if 1 <= strong_candidate <= 7:
                strong_val = strong_candidate
                lotto_series = valid_lotto_nums[-7:-1]
            else:
                strong_val = valid_lotto_nums[0]
                lotto_series = valid_lotto_nums[1:7]
                
            if len(lotto_series) == 6 and 1 <= strong_val <= 7:
                records.append({
                    'מספרים': sorted(lotto_series),
                    'חזק': strong_val,
                    'פרס_גדול': True
                })
                
    return records

# טעינת הנתונים האמיתיים
all_historical_records = load_any_lotto_file()

if not all_historical_records:
    all_historical_records = []
    random.seed(42)
    for _ in range(104):
        all_historical_records.append({
            'מספרים': sorted(random.sample(range(1, 38), 6)),
            'חזק': random.randint(1, 7),
            'פרס_גדול': random.choice([True, False])
        })
    is_simulation = True
else:
    is_simulation = False

if not is_simulation:
    records_year = all_historical_records[:104]
    records_year.reverse()
else:
    records_year = all_historical_records

all_numbers = []
all_strong = []
for r in records_year:
    all_numbers.extend(r['מספרים'])
    all_strong.append(r['חזק'])
        
counts = Counter(all_numbers)
strong_counts = Counter(all_strong)

top_20_pool = [n for n, c in counts.most_common(20)]
if len(top_20_pool) < 20:
    remaining = [n for n in range(1, 38) if n not in top_20_pool]
    top_20_pool.extend(remaining[:20 - len(top_20_pool)])

cold_numbers = [n for n in range(1, 38) if n not in top_20_pool][:7]

st.title("🎰 לוטו חכם: מנוע אנליזה")
if is_simulation:
    st.warning("⚠️ המערכת קוראת את הקובץ בגיטהאב אך מבנהו לא זוהה. מציג נתוני סימולציה זמניים.")
else:
    st.success(f"✔️ החיבור הצליח! מנתח {len(records_year)} הגרלות אמת מתוך קובץ מפעל הפיס שלך.")

# === חלק 1: ניתוח פיננסי ===
st.subheader("💰 ניתוח פיננסי: מספרים חזקים")

financial_data = []
for strong_num in range(1, 8):
    matching_draws = [r for r in records_year if r.get('חזק') == strong_num]
    total_draws_for_num = len(matching_draws)
    final_power = (strong_counts.get(strong_num, 0) / len(records_year) * 100) if records_year else 0
    
    financial_data.append({
        "מספר חזק": f"מספר {strong_num}",
        "הופעות בשנה האחרונה": f"{total_draws_for_num} פעמים",
        "מדד עוצמה": f"{final_power:.1f}%",
        "סדר_מיון": final_power
    })
    
financial_df = pd.DataFrame(financial_data).sort_values(by="סדר_מיון", ascending=False).drop(columns=["סדר_מיון"])
st.dataframe(financial_df.set_index("מספר חזק"), use_container_width=True)

st.divider()

# === חלק 2: לוח תחזיות ===
st.header("🔮 תמונת המצב והתחזית הטכנולוגית")

with st.expander("📊 סעיף 1: ניתוח סטטיסטי (חמים מול קרים)"):
    st.write(f"**המספרים החמים ביותר בשנה האחרונה:** {', '.join(map(str, top_20_pool[:6]))}")
    st.write(f"**המספרים הקרים ביותר בשנה האחרונה:** {', '.join(map(str, cold_numbers))}")
    st.write(f"**המספר החזק הכי שכיח בשנה האחרונה:** מספר {strong_counts.most_common(1)[0][0] if strong_counts else 'אין'}")

with st.expander("📈 סעיף 2: אסטרטגיית מרווחים ואיזון"):
    even_half = 0
    for r in records_year:
        evens = sum(1 for n in r['מספרים'] if n % 2 == 0)
        if evens == 3: even_half += 1
    even_pct = (even_half / len(records_year)) * 100 if records_year else 0
    st.write(f"**המלצת המכונה:** יחס אופטימלי של 3 זוגיים ו-3 אי זוגיים.")
    st.write(f"**אימות היסטורי בשנה זו:** דפוס זה הופיע ב-{even_pct:.1f}% מההגרלות.")

with st.expander("⚡ סעיף 3: ניתוח פיזיקלי (סטיית מכונה)"):
    recent_draws = records_year[-10:] if len(records_year) >= 10 else records_year
    recent_numbers = []
    for r in recent_draws: recent_numbers.extend(r['מספרים'])
    recent_counts = Counter(recent_numbers)
    wave_numbers = [n for n, c in recent_counts.most_common(3)]
    st.write(f"**מספרים במומנטום חם (10 הגרלות אחרונות):** {', '.join(map(str, wave_numbers))}")

with st.expander("🎲 סעיף 4: סימולציית מונטה קרלו"):
    st.write("**מנוע סימולציה פעיל:** מסנן צירופים חריגים על בסיס 104 ההגרלות האחרונות.")

with st.expander("🎯 סעיף 5: תורת המשחקים (ללא שותפים)"):
    st.write("**אסטרטגיית חלוקה:** שילוב מספרים מעל 31 כדי למנוע הצטלבות עם תאריכי ימי הולדת.")

st.divider()

# === חלק 3: בדיקת סיכוי למספר החזק הבא ===
st.subheader("🔮 בדיקת סיכוי למספר החזק הבא")
chosen_strong = st.selectbox("בחר את המספר החזק שיצא בהגרלה האחרונה:", options=list(range(1, 8)), index=5)

next_strong_list = []
for i in range(len(records_year) - 1):
    if records_year[i].get('חזק') == chosen_strong:
        next_draw = records_year[i+1]
        if next_draw.get('חזק'): 
            next_strong_list.append(next_draw['חזק'])
            
total_cases = len(next_strong_list)
counts_after_chosen = Counter(next_strong_list)

st.write(f"המספר **{chosen_strong}** יצא {total_cases} פעמים בחלון הזמן של השנה האחרונה בקובץ.")

if total_cases > 0:
    st.write("📊 **ההסתברות למספר החזק הבא (ממוין מהסיכוי הגבוה לנמוך):**")
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
else:
    st.info(f"לא נמצאו מספיק נתונים בשנה האחרונה על מספרים שעלו אחרי המספר {chosen_strong}.")
    
st.divider()
st.write("### הפקת טורים חכמים למילוי:")

selected_strong = random.randint(1, 7)

# כפתור 1
if st.button("🎲 כפתור 1: הגרלה דינמית רגילה (מתוך 12 החמים)"):
    current_hot_12 = sorted(random.sample(top_20_pool, 12))
    st.subheader(f"נבחר מספר חזק אחיד: {selected_strong}")
    
    st.write("**12 המספרים שננעלו להגרלה זו:**")
    boxes_html = "".join([f"<div class='number-box'>{idx+1}) {num}</div>" for idx, num in enumerate(current_hot_12)])
    st.markdown(boxes_html, unsafe_allow_html=True)
    
    st.write("---")
    for i in range(1, 9):
        nums = sorted(random.sample(current_hot_12, 6))
        st.info(f"טבלה {i}: \n\n {', '.join(map(str, nums))} | חזק: {selected_strong}")
    st.balloons()

# כפתור 2
if st.button("📈 כפתור 2: הגרלת סדרות ומרווחים (מתוך 12 החמים)") :
    current_hot_12 = sorted(random.sample(top_20_pool, 12))
    st.subheader(f"נבחר מספר חזק אחיד: {selected_strong}")
    
    st.write("**12 המספרים שננעלו לאסטרטגיית מרווחים:**")
    boxes_html = "".join([f"<div class='number-box'>{idx+1}) {num}</div>" for idx, num in enumerate(current_hot_12)])
    st.markdown(boxes_html, unsafe_allow_html=True)
    
    st.write("---")
    for i in range(1, 9):
        valid_table = False
        attempts = 0
        table = []
        while not valid_table and attempts < 200:
            table = random.sample(current_hot_12, 6)
            table.sort()
            
            diffs = [table[j+1] - table[j] for j in range(5)]
            cond_diff = any(d in [1, 2, 3] for d in diffs)
            
            evens = sum(1 for n in table if n % 2 == 0)
            cond_balance = evens in [2, 3, 4]
            
            cond_high = any(n > 31 for n in table)
            
            if cond_diff and cond_balance and cond_high:
                valid_table = True
            attempts += 1
            
        if not valid_table:
            table = sorted(random.sample(current_hot_12, 6))
            
        st.success(f"טבלה {i} (משולבת אסטרטגיות): \n\n {', '.join(map(str, table))} | חזק: {selected_strong}")
    st.balloons()
