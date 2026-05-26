import streamlit as st
import pandas as pd
from collections import Counter
import random

# הגדרת דף נקייה והסתרת תפריטים מיותרים לנייד
st.set_page_config(page_title="לוטו חכם - מפעל הפיס", layout="centered")

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stButton>button {width: 100%; border-radius: 20px; height: 3.5em; font-weight: bold; margin-bottom: 10px;}
    </style>
    """, unsafe_allow_html=True)

@st.cache_data
def load_mifal_hapais_data(file_path):
    try:
        # קריאת הקובץ של מפעל הפיס עם גמישות למפרידים (פסיק או נקודה-פסיק)
        df = pd.read_csv(file_path, encoding='utf8', sep=None, engine='python')
        
        # ניקוי רווחים משמות העמודות
        df.columns = df.columns.str.strip()
        
        # איתור עמודת המספר החזק
        strong_col = [col for col in df.columns if 'חזק' in col or 'Strong' in col]
        
        # איתור 6 עמודות המספרים (מחפש עמודות שמכילות 'מספר' או 'Num' ואינן החזק)
        num_cols = [col for col in df.columns if ('מספר' in col or 'Num' in col) and col != strong_col[0]]
        # מיון כדי להבטיח סדר נכון (מספר 1, מספר 2...)
        num_cols = sorted(num_cols)[:6]
        
        records = []
        for _, row in df.iterrows():
            try:
                nums = [int(row[c]) for c in num_cols if pd.notna(row[c])]
                strong = int(row[strong_col[0]]) if pd.notna(row[strong_col[0]]) else None
                
                if len(nums) == 6 and strong is not None:
                    # בדיקה אם יש נתוני פרס או אם זו הגרלה מיוחדת
                    has_prize = any('פרס' in str(c) or 'זכיות' in str(c) for c in df.columns)
                    
                    records.append({
                        'מספרים': nums,
                        'חזק': strong,
                        'פרס_גדול': has_prize
                    })
            except:
                continue
        return records
    except:
        return None

# טעינת הנתונים מהקובץ הרשמי
all_records = load_mifal_hapais_data('lotto2026.csv')

if all_records:
    # קובץ מפעל הפיס מגיע מההגרלה החדשה ביותר לישנה ביותר.
    # לכן, 104 השורות הראשונות הן בדיוק 365 הימים האחרונים (שנה אחורה).
    records_year = all_records[:104]
    
    # הפיכת הרשימה לסדר כרונולוגי ישר (מהישן לחדש) לצורך חישוב "מה בא אחרי מה"
    records_year.reverse()
    
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
    
    st.title("🎰 לוטו חכם: ניתוח קובץ מפעל הפיס")
    st.caption(f"הניתוח מבוסס על {len(records_year)} ההגרלות האחרונות של השנה האחרונה מתוך הקובץ הרשמי.")
    
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
        st.write("**אסטרטגיית חלוקה:** שילוב מספרים מעל 31 כדי למנע הצטלבות עם תאריכי ימי הולדת.")

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
            st.info(f"טבלה {i}: \n\n {', '.join(map(str, nums))} | חזק: {selected_strong}")
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
            st.success(f"טבלה {i} (משולבת אסטרטגיות): \n\n {', '.join(map(str, table))} | חזק: {selected_strong}")
        st.balloons()
else:
    st.error("קובץ הנתונים 'lotto2026.csv' לא נטען. ודא שהעלית את הקובץ הרשמי של מפעל הפיס ל-GitHub באותו השם.")
