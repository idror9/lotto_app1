import streamlit as st
import pandas as pd
from collections import Counter
import random

# הגדרת דף נקייה והסתרת תפריטים מיותרים לנייד
st.set_page_config(page_title="לוטו חכם - אבחון סופי", layout="centered")

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stButton>button {width: 100%; border-radius: 20px; height: 3.5em; font-weight: bold; margin-bottom: 10px;}
    </style>
    """, unsafe_allow_html=True)

@st.cache_data
def load_mifal_hapais_strict(file_path):
    # רשימת קידודים נפוצים לקבצי עברית
    for enc in ['windows-1255', 'utf-8', 'ansi']:
        try:
            # קריאה ישירה של הקובץ
            df = pd.read_csv(file_path, encoding=enc, sep=None, engine='python')
            df.columns = df.columns.str.strip()
            
            # בדיקה אם קיימות עמודות שמכילות מספרים
            records = []
            
            # זיהוי עמודת המספר החזק (עמודה שמכילה ערכים בין 1 ל-7)
            strong_col = None
            for col in df.columns:
                if 'חזק' in str(col) or 'strong' in str(col).lower():
                    strong_col = col
                    break
            
            # זיהוי 6 עמודות המספרים
            num_cols = [col for col in df.columns if ('מספר' in str(col) or 'num' in str(col).lower()) and col != strong_col]
            num_cols = sorted(num_cols)[:6]
            
            # אם לא נמצאו עמודות לפי שם, ננסה לפי מיקום קבוע (למשל עמודות 2 עד 8)
            if not strong_col or len(num_cols) < 6:
                # ניסיון חילוץ לפי מיקומי עמודות גנריים בקובץ מפעל הפיס
                # עמודה 0: מספר הגרלה, עמודה 1: תאריך, עמודות 2-7: מספרים, עמודה 8: מספר חזק
                num_cols = list(df.columns[2:8])
                strong_col = df.columns[8]
            
            for _, row in df.iterrows():
                try:
                    vals = [int(row[c]) for c in num_cols if pd.notna(row[c])]
                    st_val = int(row[strong_col]) if pd.notna(row[strong_col]) else None
                    if len(vals) == 6 and st_val is not None:
                        records.append({'מספרים': vals, 'חזק': st_val})
                except:
                    continue
                    
            if records:
                return records, None
        except Exception as e:
            continue
            
    # אם הגענו לכאן, ננסה לקרוא את השורות הראשונות כטקסט כדי להציג למשתמש
    try:
        with open(file_path, 'r', encoding='windows-1255', errors='ignore') as f:
            lines = [f.readline() for _ in range(4)]
        return None, lines
    except:
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = [f.readline() for _ in range(4)]
            return None, lines
        except:
            return None, ["לא ניתן לקרוא את הקובץ כלל כטקסט"]

# טעינת הנתונים
all_records, raw_lines_preview = load_mifal_hapais_strict('lotto2026.csv')

if all_records:
    records_year = all_records[:104]
    records_year.reverse()
    
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
    st.caption(f"הנתונים פוענחו בהצלחה! מציג אנליזה עבור {len(records_year)} ההגרלות האחרונות.")
    
    # === חלק 1: ניתוח פיננסי ===
    st.subheader("💰 ניתוח פיננסי: מספרים חזקים")
    financial_data = []
    for strong_num in range(1, 8):
        total_draws_for_num = sum(1 for r in records_year if r.get('חזק') == strong_num)
        chance = (strong_counts.get(strong_num, 0) / len(records_year) * 100) if records_year else 0
        financial_data.append({
            "מספר חזק": f"מספר {strong_num}",
            "הופעות בשנה האחרונה": f"{total_draws_for_num} פעמים",
            "מדד עוצמה": f"{chance:.1f}%",
            "סדר": chance
        })
    financial_df = pd.DataFrame(financial_data).sort_values(by="סדר", ascending=False).drop(columns=["סדר"])
    st.dataframe(financial_df.set_index("מספר חזק"), use_container_width=True)
    
    st.divider()
    
    # === חלק 2: לוח תחזיות ===
    st.header("🔮 תמונת המצב הסטטיסטית")
    with st.expander("📊 ניתוח חמים מול קרים"):
        st.write(f"**המספרים החמים ביותר:** {', '.join(map(str, top_20_pool[:6]))}")
        st.write(f"**המספרים הקרים ביותר:** {', '.join(map(str, cold_numbers))}")
        
    st.divider()
    st.write("### הפקת טורים חכמים למילוי:")
    selected_strong = random.randint(1, 7)

    if st.button("🎲 כפתור 1: הגרלה דינמית רגילה"):
        current_hot_12 = random.sample(top_20_pool, 12)
        st.subheader(f"מספר חזק שנבחר: {selected_strong}")
        for i in range(1, 9):
            nums = sorted(random.sample(current_hot_12, 6))
            st.info(f"טבלה {i}: {', '.join(map(str, nums))} | חזק: {selected_strong}")
            
    if st.button("📈 כפתור 2: הגרלת סדרות ומרווחים"):
        current_hot_12 = random.sample(top_20_pool, 12)
        st.subheader(f"מספר חזק שנבחר: {selected_strong}")
        for i in range(1, 9):
            table = sorted(random.sample(current_hot_12, 6))
            st.success(f"טבלה {i}: {', '.join(map(str, table))} | חזק: {selected_strong}")
else:
    st.error("❌ שגיאה בפענוח מבנה הקובץ")
    st.write("כדי שנוכל לתקן את זה מיד, העתק והדבק לי כאן את השורות הראשונות של הקובץ כפי שהן מופיעות בריבוע הבא:")
    if raw_lines_preview:
        st.code("".join(raw_lines_preview))
