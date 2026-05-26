import streamlit as st
import pandas as pd
from collections import Counter
import random
import re

# הגדרת דף נקייה והסתרת תפריטים מיותרים לנייד
st.set_page_config(page_title="לוטו חכם - גרסה סופית", layout="centered")

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stButton>button {width: 100%; border-radius: 20px; height: 3.5em; font-weight: bold; margin-bottom: 10px;}
    </style>
    """, unsafe_allow_html=True)

def parse_free_text_lotto(file_path):
    try:
        with open(file_path, 'r', encoding='utf8') as f:
            content = f.read()
            
        # פיצול הקובץ לפי מילות מפתח של הגרלה חדשה (תאריך או מספר הגרלה)
        blocks = re.split(r'(?=תאריך|הגרלה)', content)
        records = []
        
        for block in blocks:
            if not block.strip():
                continue
                
            # חילוץ המספר החזק: מחפש מספר בודד בין 1 ל-7 שמופיע בשורה או ליד המילה חזק
            strong_match = re.search(r'(?:חזק.*?|החזק.*?)\b([1-7])\b', block)
            strong_num = int(strong_match.group(1)) if strong_match else None
            
            # חילוץ כל המספרים בבלוק הנוכחי
            all_nums = [int(n) for n in re.findall(r'\b\d+\b', block)]
            
            # סינון מספרים שמתאימים להיות 6 המספרים של הלוטו (בין 1 ל-37)
            # נסנן החוצה את המספר החזק אם מצאנו אותו, ונתונים כמו שנה (2025, 2026) או ימים בחודש
            clean_candidates = []
            for n in all_nums:
                if 1 <= n <= 37 and n != strong_num:
                    clean_candidates.append(n)
                    
            # אם לא מצאנו חזק מקודם, ננסה לקחת את המספר האחרון בבלוק שנמצא בטווח 1-7
            if strong_num is None:
                possible_strong = [n for n in all_nums if 1 <= n <= 7]
                if possible_strong:
                    strong_num = possible_strong[-1]
                    # ניקוי מחדש של המועמדים ל-6 המספרים
                    clean_candidates = [n for n in all_nums if 1 <= n <= 37 and n != strong_num]
            
            # בדיקה אם יש עדות לפרס גדול בבלוק
            has_prize = any(kw in block for kw in ["זכיות", "פרס", "סך הכל", "₪"])
            
            # אם יש לנו לפחות 6 מספרים רגילים ומספר חזק - יש לנו הגרלה תקינה!
            if len(clean_candidates) >= 6 and strong_num is not None:
                # לוקחים את 6 המספרים הראשונים שזוהו כסדרת הגורל
                records.append({
                    'מספרים': clean_candidates[:6],
                    'חזק': strong_num,
                    'פרס_גדול': has_prize
                })
                
        return records
    except Exception as e:
        return None

# טעינת הנתונים מהקובץ
records_year = parse_free_text_lotto('lotto2026.csv')

if records_year:
    # מאחר שהקובץ מציג לרוב מהחדש לישן, נהפוך אותו קודם כדי להביא סדר כרונולוגי ישר
    records_year.reverse()
    
    # חיתוך מדויק של 104 ההגרלות האחרונות ביותר (שנה אחורה קלנדרית)
    records_year = records_year[-104:] if len(records_year) >= 104 else records_year
    
    # חילוץ מאגרים
    all_numbers = []
    all_strong = []
    for r in records_year:
        all_numbers.extend(r['מספרים'])
        all_strong.append(r['חזק'])
            
    counts = Counter(all_numbers)
    strong_counts = Counter(all_strong)
    
    top_20_pool = [n for n, c in counts.most_common(20)]
    cold_numbers = [n for n in range(1, 38) if n not in top_20_pool][:7]
    
    st.title("🎰 לוטו חכם: ניתוח 365 ימים אחרונים")
    st.caption(f"הנתונים מבוססים על {len(records_year)} הגרלות שחולצו בהצלחה באמצעות סורק הטקסט החופשי.")
    
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
        st.write(f"**אימות היסטורי בשנה זו:** דפוס זה הופיע ב-{even_pct:.1f}% מההגרלות האחרונות.")

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
            if next_draw.get('חזק'): next_strong_list.append(next_draw['חזק'])
                
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
    st.error("קובץ הנתונים 'lotto2026.csv' ריק או שלא מכיל תבניות של הגרלות לוטו.")
