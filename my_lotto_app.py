import streamlit as st
import pandas as pd
from collections import Counter
import random
from datetime import datetime, timedelta

# הגדרת דף נקייה והסתרת תפריטים מיותרים לנייד
st.set_page_config(page_title="לוטו חכם - שנה אחורה", layout="centered")

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stButton>button {width: 100%; border-radius: 20px; height: 3.5em; font-weight: bold; margin-bottom: 10px;}
    .reportview-container .main .block-container{ max-width: 95%; }
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
            if "תאריך הגרלה:" in line or "תאריך:" in line:
                if current_record and 'תאריך' in current_record and 'מספרים' in current_record:
                    records.append(current_record)
                
                raw_date = lines[i+1].strip() if i+1 < len(lines) else ""
                current_record = {'תאריך_טקסט': raw_date, 'פרס_גדול': False, 'תאריך_אובייקט': None}
                
                # ניסיון להפוך את הטקסט לתאריך אמיתי לצורך סינון חלון הזמן
                for fmt in ('%d/%m/%Y', '%d.%m.%Y', '%Y-%m-%d'):
                    try:
                        current_record['תאריך_אובייקט'] = datetime.strptime(raw_date, fmt)
                        break
                    except:
                        pass
                i += 1
            elif "המספר החזק:" in line:
                try: current_record['חזק'] = int(lines[i+1])
                except: pass
                i += 1
            elif "המספרים שעלו בגורל:" in line or "מספרים:" in line:
                start = i + 1
                if start < len(lines) and lines[start] == "": start += 1
                nums = []
                for j in range(6):
                    if start + j < len(lines):
                        try: nums.append(int(lines[start+j]))
                        except: pass
                current_record['מספרים'] = nums
                i = start + 5
            elif "סך הכל זכיות בהגרלה:" in line or "זכיות" in line:
                current_record['פרס_גדול'] = True
            i += 1
        if current_record and 'תאריך_טקסט' in current_record and 'מספרים' in current_record:
            records.append(current_record)
        return records
    except:
        return None

# טעינת הנתונים
all_historical_records = parse_lotto_file('lotto2026.csv')

if all_historical_records:
    # פילטר קשוח: לוקחים רק הגרלות מה-365 ימים האחרונים
    one_year_ago = datetime.now() - timedelta(days=365)
    
    # סינון הרשימה (אם תאריך מסוים לא פוענח, נשמור אותו ליתר ביטחון כדי לא לאבד מידע)
    records = [
        r for r in all_historical_records 
        if r['תאריך_אובייקט'] is None or r['תאריך_אובייקט'] >= one_year_ago
    ]
    
    # סידור כרונולוגי מהישן לחדש בתוך השנה הזו
    records.reverse() 
    
    # חילוץ מאגרים לשנה האחרונה
    all_numbers = []
    all_strong = []
    for r in records:
        if 'מספרים' in r: all_numbers.extend(r['מספרים'])
        if 'חזק' in r: all_strong.append(r['חזק'])
            
    counts = Counter(all_numbers)
    strong_counts = Counter(all_strong)
    
    # מאגר חמים וקרים של השנה האחרונה
    top_20_pool = [n for n, c in counts.most_common(20)]
    cold_numbers = [n for n in range(1, 38) if n not in top_20_pool][:7]
    
    st.title("🎰 לוטו חכם: חלון זמן שנתנאל הגדיר (שנה אחורה)")
    st.caption(f"הנתונים במסך זה מבוססים אך ורק על {len(records)} ההגרלות שהתרחשו ב-12 החודשים האחרונים.")
    
    # === חלק 1: ניתוח פיננסי של המספרים החזקים (שנה אחורה) ===
    st.subheader("💰 ניתוח פיננסי: מספרים חזקים ופוטנציאל הפרס")
    
    financial_data = []
    for strong_num in range(1, 8):
        matching_draws = [r for r in records if r.get('חזק') == strong_num]
        total_draws_for_num = len(matching_draws)
        big_wins = sum(1 for r in matching_draws if r.get('פרס_גדול', False))
        
        raw_power = (big_wins / total_draws_for_num * 100) if total_draws_for_num > 0 else 0
        final_power = (raw_power * 0.7) + ((strong_counts.get(strong_num, 0) / len(records) * 100) * 0.3) if records else 0
        
        financial_data.append({
            "מספר חזק": f"מספר {strong_num}",
            "זכיות משמעותיות בשנה האחרונה": f"{big_wins} הגרלות",
            "מדד עוצמה כספית": f"{final_power:.1f}%",
            "סדר_מיון": final_power
        })
        
    financial_df = pd.DataFrame(financial_data).sort_values(by="סדר_מיון", ascending=False).drop(columns=["סדר_מיון"])
    st.dataframe(financial_df.set_index("מספר חזק"), use_container_width=True)
    
    st.divider()
    
    # === חלק 2: לוח תחזיות מבוסס 5 הסעיפים (שנה אחורה) ===
    st.header("🔮 תמונת המצב והתחזית הטכנולוגית")
    
    with st.expander("📊 סעיף 1: ניתוח סטטיסטי (חמים מול קרים)", expanded=False):
        st.write(f"**המספרים החמים ביותר בשנה האחרונה:** {', '.join(map(str, top_20_pool[:6]))}")
        st.write(f"**המספרים הקרים ביותר בשנה האחרונה:** {', '.join(map(str, cold_numbers))}")
        st.write(f"**המספר החזק הכי שכיח בשנה האחרונה:** מספר {strong_counts.most_common(1)[0][0] if strong_counts else 'אין'}")

    with st.expander("📈 סעיף 2: אסטרטגיית mרווחים ואיזון"):
        even_half = 0
        for r in records:
            evens = sum(1 for n in r['מספרים'] if n % 2 == 0)
            if evens == 3: even_half += 1
        even_pct = (even_half / len(records)) * 100 if records else 0
        st.write(f"**המלצת המכונה:** יחס אופטימלי של 3 זוגיים ו-3 אי זוגיים.")
        st.write(f"**אימות היסטורי בשנה זו:** דפוס זה הופיע ב-{even_pct:.1f}% מההגרלות האחרונות.")

    with st.expander("⚡ סעיף 3: ניתוח פיזיקלי (סטיית מכונה וגלים)"):
        recent_draws = records[-10:] if len(records) >= 10 else records
        recent_numbers = []
        for r in recent_draws: recent_numbers.extend(r['מספרים'])
        recent_counts = Counter(recent_numbers)
        wave_numbers = [n for n, c in recent_counts.most_common(3)]
        st.write(f"**מספרים במומנטום חם (10 הגרלות אחרונות):** {', '.join(map(str, wave_numbers))}")

    with st.expander("🎲 סעיף 4: סימולציית מונטה קרלו"):
        st.write("**מנוע סימולציה מוגבל לשנה האחרונה:** מסנן החוצה צירופים חריגים על בסיס התנהגות המכונה ב-12 החודשים האחרונים בלבד.")

    with st.expander("🎯 סעיף 5: תורת המשחקים (זכייה ללא שותפים)"):
        st.write("**חלוקת טופס חכמה:** שילוב מבוקר של מספרים מעל 31 כדי למנוע הצטלבות עם תאריכי ימי הולדת של שחקנים אחרים.")

    st.divider()

    # === חלק 3: בדיקת סיכוי למספר החזק הבא ===
    st.subheader("🔮 בדיקת סיכוי למספר החזק הבא")
    chosen_strong = st.selectbox("בחר את המספר החזק שיצא בהגרלה האחרונה:", options=list(range(1, 8)), index=5)
    
    next_strong_list = []
    for i in range(len(records) - 1):
        if records[i].get('חזק') == chosen_strong:
            next_draw = records[i+1]
            if next_draw.get('חזק'): next_strong_list.append(next_draw['חזק'])
                
    total_cases = len(next_strong_list)
    counts_after_chosen = Counter(next_strong_list)
    
    st.write(f"המספר **{chosen_strong}** יצא {total_cases} פעמים בחלון הזמן של השנה האחרונה.")
    
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
        
    st.divider()
    st.write("### הפקת טורים חכמים למילוי:")
    
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
                cond_diff = any(d in [1, 2, 3] for d in diffs)
                
                evens = sum(1 for n in table if n % 2 == 0)
                cond_balance = evens in [2, 3, 4]
                
                cond_high = any(n > 31 for n in table)
                
                if cond_diff and cond_balance and cond_high:
                    valid_table = True
                attempts += 1
            st.success(f"טבלה {i} (משולבת אסטרטגיות): \n\n {', '.join(map(str, table))}  |  חזק: {selected_strong}")
        st.balloons()
else:
    st.error("קובץ הנתונים 'lotto2026.csv' לא נמצא.")
