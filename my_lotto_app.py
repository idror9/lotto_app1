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
    # רשימת קידודים אפשריים לקבצי מפעל הפיס
    encodings = ['utf-8', 'windows-1255', 'ansi', 'utf-8-sig']
    df = None
    
    for enc in encodings:
        try:
            df = pd.read_csv(file_path, encoding=enc, sep=None, engine='python')
            break
        except:
            continue
            
    if df is None:
        return None

    try:
        # ניקוי רווחים ותווים סמויים משמות העמודות
        df.columns = df.columns.str.strip().str.replace('\ufeff', '')
        
        # איתור עמודת המספר החזק (גמישות למילים חלקיות)
        strong_col = [col for col in df.columns if 'חזק' in col or 'Strong' in col]
        if not strong_col:
            return None
            
        # איתור 6 עמודות המספרים
        num_cols = [col for col in df.columns if ('מספר' in col or 'Num' in col) and col != strong_col[0]]
        num_cols = sorted(num_cols)[:6]
        
        if len(num_cols) < 6:
            return None
            
        records = []
        for _, row in df.iterrows():
            try:
                nums = [int(row[c]) for c in num_cols if pd.notna(row[c])]
                strong = int(row[strong_col[0]]) if pd.notna(row[strong_col[0]]) else None
                
                if len(nums) == 6 and strong is not None:
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

# טעינת הנתונים
all_records = load_mifal_hapais_data('lotto2026.csv')

if all_records:
    # לקיחת 104 ההגרלות האחרונות (שנה אחורה)
    records_year = all_records[:104]
    records_year.reverse()
    
    all_numbers = []
    all_strong = []
    for r in records_year:
        all_numbers.extend(r['מספרים'])
        all_strong.append(r['חजק'])
            
    counts = Counter(all_numbers)
    strong_counts = Counter(all_strong)
    
    top_20_pool = [n for n, c in counts.most_common(20)]
    cold_numbers = [n for n in range(1, 38) if n not in top_20_pool][:7]
    
    st.title("🎰 לוטו חכם: ניתוח קובץ מפעל הפיס")
    st.caption(f"הניתוח מבוסס על {len(records_year)} ההגרלות האחרונות של השנה האחרונה.")
    
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

    st.divider()
    st.write("### הפקת טורים חכמים למילוי:")
    
    selected_strong = random.randint(1, 7)

    if st.button("🎲 כפתור 1: הגרלה דינמית רגילה"):
        current_hot_12 = random.sample(top_20_pool, 12)
        st.subheader(f"נבחר מספר חזק אחיד: {selected_strong}")
        for i in range(1, 9):
            nums = sorted(random.sample(current_hot_12, 6))
            st.info(f"טבלה {i}: {', '.join(map(str, nums))} | חזק: {selected_strong}")
        st.balloons()

    if st.button("📈 כפתור 2: הגרלת סדרות ומרווחים"):
        current_hot_12 = random.sample(top_20_pool, 12)
        st.subheader(f"נבחר מספר חזק אחיד: {selected_strong}")
        for i in range(1, 9):
            table = sorted(random.sample(current_hot_12, 6))
            st.success(f"טבלה {i}: {', '.join(map(str, table))} | חזק: {selected_strong}")
        st.balloons()
else:
    st.error("קובץ הנתונים לא נטען. אנא ודא ששם הקובץ ב-GitHub הוא בדיוק lotto2026.csv באותיות קטנות ושאינו ריק.")
