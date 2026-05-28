import streamlit as st
import pandas as pd
from collections import Counter
import random
import os
import re

# הגדרת דף נקייה והסתרת תפריטים מיותרים לנייד
st.set_page_config(page_title="לוטו חכם - רקע כחול רך", layout="centered")

# קוד עיצוב ליישור מוחלט מימין לשמאל (RTL), התאמה לנייד ושינוי רקע התיבות לכחול נוח לעיניים
st.markdown("""
    <style>
    html, body, [data-testid="stAppViewContainer"] {
        direction: RTL;
        text-align: right;
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    .stButton>button {
        width: 100%; 
        border-radius: 20px; 
        height: 3.5em; 
        font-weight: bold; 
        margin-bottom: 10px;
    }
    
    div[data-testid="stMarkdownContainer"] p, h1, h2, h3, h4, h5, h6 {
        text-align: right;
        direction: RTL;
    }
    div[data-testid="stSelectbox"] label {
        text-align: right;
        width: 100%;
    }
    div[data-testid="stSelectbox"] div[data-baseweb="select"] {
        direction: RTL;
        text-align: right;
    }
    div[data-testid="stDataFrame"] {
        direction: RTL;
        text-align: right;
    }
    
    /* רקע כחול פסטל רך ונוח לעיניים עבור תיבות הטורים */
    .ticket-box {
        background-color: #e6f0fa;
        border: 2px solid #a3c2e0;
        border-right: 6px solid #1e88e5;
        padding: 12px;
        margin: 8px 0px;
        border-radius: 0px 10px 10px 0px;
        font-weight: bold;
        color: #0b2545;
        text-align: right;
        box-shadow: 0px 2px 4px rgba(0,0,0,0.05);
    }
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

# === חלק 2: לוח
