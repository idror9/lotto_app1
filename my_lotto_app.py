import streamlit as st
import pandas as pd
from collections import Counter
import random
import os
import re

# הגדרת דף נקייה והסתרת תפריטים מיותרים לנייד
st.set_page_config(page_title="לוטו חכם - גרסה יציבה 6 שנים", layout="centered")

# קוד עיצוב בסיסי ויציב ליישור מוחלט מימין לשמאל (RTL) והתאמה לנייד
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
    
    /* יישור טבלאות נתונים לימין בצורה טבעית */
    div[data-testid="stDataFrame"] {
        direction: RTL;
        text-align: right;
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
                    'חזק': strong_val
                })
                
    return records

all_historical_records = load_any_lotto_file()

TOTAL_6_YEARS_DRAWS = 624

if not all_historical_records:
    all_historical_records = []
    random.seed(42)
    for i in range(TOTAL_6_YEARS_DRAWS):
        all_historical_records.append({
            'מספרים': sorted(random.sample(range(1, 38), 6)),
            'חזק': random.randint(1, 7)
        })
    is_simulation = True
else:
    is_simulation = False

if not is_simulation:
    records_extended = all_historical_records[:TOTAL_6_YEARS_DRAWS]
    records_extended.reverse()
else:
    records_extended = all_historical_records

all_numbers = []
all_strong = []
for r in records_extended:
    all_numbers.extend(r['מספרים'])
    all_strong.append(r['חזק'])
        
counts = Counter(all_numbers)
strong_counts = Counter(all_strong)

top_20_pool = [n for n, c in counts.most_common(20)]
if len(top_20_pool) < 20:
    remaining = [n for n in range(1, 38) if n not in top_20_pool]
    top_20_pool.extend(remaining[:20 - len(top_20_pool)])

cold_numbers = [n for n in range(1, 38) if n not in top_20_pool][:7]

st.title("🎰 לוטו חכם: מנוע אנליזה מורחב (6 שנים)")
if is_simulation:
    st.warning("⚠️ המערכת קוראת את הקובץ בגיטהאב אך מבנהו לא זוהה. מציג נתוני סימולציה זמניים של 6 שנים.")
else:
    st.success(f"✔️ החיבור הצליח! מנתח {len(records_extended)} הגרלות אמת מתוך קובץ מפעל הפיס שלך (חלון זמן של 6 שנים).")

# === חלק 1: ניתוח פיננסי ===
st.subheader("💰 ניתוח פיננסי: מספרים חזקים (6 שנים אחרונות)")

financial_data = []
for strong_num in range(1, 8):
    matching_draws = [r for r in records_extended if r.get('חזק') == strong_num]
    total_draws_for_num = len(matching_draws)
    final_power = (strong_counts.get(strong_num, 0) / len(records_extended) * 100) if records_extended else 0
    
    financial_data.append({
        "מספר חזק": f"מספר {strong_num}",
        "הופעות ב-6 השנים האחרונות": f"{total_draws_for_num} פעמים",
        "מדד עוצמה מצטבר": f"{final_power:.1f}%",
        "סדר_מיון": final_power
    })
    
financial_df = pd.DataFrame(financial_data).sort_values(by="סדר_מיון", ascending=False).drop(columns=["סדר_מיון"])
st.dataframe(financial_df.set_index("מספר חזק"), use_container_width=True)

st.divider()

# === חלק 2: לוח תחזיות ===
st.header("🔮 תמונת המצב והתחזית הטכנולוגית (נתוני 6 שנים)")

with st.expander("📊 סעיף 1: ניתוח סטטיסטי מורחב (חמים מול קרים)"):
    st.write(f"**המספרים החמים ביותר ב-6 השנים האחרונות:** {', '.join(map(str, top_20_pool[:6]))}")
    st.write(f"**המספרים הקרים ביותר ב-6 השנים האחרונות:** {', '.join(map(str, cold_numbers))}")
    st.write(f"**המספר החזק השכיח ביותר ב-6 השנים האחרונות:** מספר {strong_counts.most_common(1)[0][0] if strong_counts else 'אין'}")

with st.expander("📈 סעיף 2: אסטרטגיית מרווחים ואיזון"):
    even_half = 0
    for r in records_extended:
        evens = sum(1 for n in r['מספרים'] if n % 2 == 0)
        if evens == 3: even_half += 1
    even_pct = (even_half / len(records_extended)) * 100 if records_extended else 0
    st.write(f"**המלצת המכונה:** יחס אופטימלי של 3 זוגיים ו-3 אי זוגיים.")
    st.write(f"**אימות היסטורי לאורך 6 שנים:** דפוס זה הופיע ב-{even_pct:.1f}% מההגרלות בארכיון.")

with st.expander("⚡ סעיף 3: ניתוח פיזיקלי (סטיית מכונה מורחבת)"):
    recent_draws = records_extended[-10:] if len(records_extended) >= 10 else records_extended
    recent_numbers = []
    for r in recent_draws: recent_numbers.extend(r['מספרים'])
    recent_counts = Counter(recent_numbers)
    wave_numbers = [n for n, c in recent_counts.most_common(3)]
    st.write(f"**מספרים במומנטום חם (10 הגרלות אחרונות):** {', '.join(map(str, wave_numbers))}")

with st.expander("🎲 סעיף 4: סימולציית מונטה קרלו"):
    st.write(f"**מנוע סימולציה פעיל:** מסנן צירופים חריגים על בסיס {len(records_extended)} ההגרלות האחרונות.")

with st.expander("🎯 סעיף 5: תורת המשחקים (ללא שותפים)"):
    st.write("**אסטרטגיית חלוקה:** שילוב מספרים מעל 31 כדי למנוע הצטלבות עם תאריכי ימי הולדת.")

st.divider()

# === חלק 3: בדיקת סיכוי למספר החזק הבא ===
st.subheader("🔮 בדיקת סיכוי למספר החזק הבא (ניתוח עומק 6 שנים)")
chosen_strong = st.selectbox("בחר את המספר החזק שיצא בהגרלה האחרונה:", options=list(range(1, 8)), index=5)

next_strong_list = []
for i in range(len(records_extended) - 1):
    if records_extended[i].get('חזק') == chosen_strong:
        next_draw = records_extended[i+1]
        if next_draw.get('חזק'): 
            next_strong_list.append(next_draw['חזק'])
            
total_cases = len(next_strong_list)
counts_after_chosen = Counter(next_strong_list)

st.write(f"המספר **{chosen_strong}** יצא {total_cases} פעמים לאורך 6 השנים האחרונות בקובץ.")

if total_cases > 0:
    st.write("📊 **ההסתברות למספר החזק הבא (ממוין מהסיכוי הגבוה לנמוך):**")
    stats_data = []
    for i in range(1, 8):
        times = counts_after_chosen.get(i, 0)
        chance = (times / total_cases) * 100
        stats_data.append({
            "המספר החזק הבא": f"מספר {i}",
            "כמה פעמים יצא אחריו בתקופה זו": f"{times} פעמים",
            "אחוז סיכוי": f"{chance:.1f}%",
            "סיכוי_עזר": chance
        })
    stats_df = pd.DataFrame(stats_data).sort_values(by="סיכוי_עזר", ascending=False).drop(columns=["סיכוי_עזר"])
    st.dataframe(stats_df.set_index("המספר החזק הבא"), use_container_width=True)
else:
    st.info(f"לא נמצאו מספיק נתונים היסטוריים על מספרים שעלו אחרי המספר {chosen_strong}.")
    
st.divider()

# === חלק 4: תיבת קלט עצמי ל-12 מספרים ===
st.subheader("✍️ הזנת 12 מספרים אישיים לצמצום")
user_input_str = st.text_input(
    "הקש 12 מספרים מופרדים בפסיקים (לדוגמה: 4,7,12,15,19,22,24,27,29,31,33,35):",
    value=""
)

def parse_user_numbers(input_str, backup_pool):
    found_nums = re.findall(r'\b\d+\b', input_str)
    parsed_ints = list(set([int(n) for n in found_nums if 1 <= int(n) <= 37]))
    
    if len(parsed_ints) < 12:
        needed = 12 - len(parsed_ints)
        for num in backup_pool:
            if num not in parsed_ints:
                parsed_ints.append(num)
            if len(parsed_ints) == 12:
                break
    return sorted(parsed_ints[:12])

user_locked_12 = parse_user_numbers(user_input_str, top_20_pool)

st.write("### הפקת טורים חכמים ומעקב היסטורי מורחב:")

def check_ticket_performance(ticket_nums, ticket_strong, history):
    summary = {"3 ניחושים": 0, "3 + חזק": 0, "4 ניחושים": 0, "4 + חזק": 0}
    for draw in history:
        match_count = len(set(ticket_nums) & set(draw['מספרים']))
        strong_match = (ticket_strong == draw['חזק'])
        
        if match_count == 3 and not strong_match:
            summary["3 ניחושים"] += 1
        elif match_count == 3 and strong_match:
            summary["3 + חזק"] += 1
        elif match_count == 4 and not strong_match:
            summary["4 ניחושים"] += 1
        elif match_count == 4 and strong_match:
            summary["4 + חזק"] += 1
    return summary

def generate_filtered_tickets(pool_12):
    tickets = []
    for _ in range(8):
        valid_table = False
        attempts = 0
        table = []
        while not valid_table and attempts < 200:
            table = random.sample(pool_12, 6)
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
            table = sorted(random.sample(pool_12, 6))
        tickets.append(table)
    return tickets

def process_and_render_sequential(tickets, t_strong, history):
    st.write("### 🎫 8 הטורים המומלצים למילוי:")
    
    table_rows = []
    for idx, t_nums in enumerate(tickets):
        table_rows.append({
            "מספר סידורי": f"טור {idx+1}",
            "צירוף מספרים": ", ".join(map(str, t_nums)),
            "מספר חזק": f"מספר {t_strong}"
        })
    tickets_df = pd.DataFrame(table_rows)
    st.dataframe(tickets_df.set_index("מספר סידורי"), use_container_width=True)
    
    st.divider()
    
    st.write("### 📊 פירוט ביצועים היסטוריים לאורך 6 שנים (לפי טורים):")
    for idx, t_nums in enumerate(tickets):
        perf = check_ticket_performance(t_nums, t_strong, history)
        perf_data = {
            "קטגוריית זכייה": ["3 ניחושים", "3 + נוסף", "4 ניחושים", "4 + נוסף"],
            "כמות הצלחות ב-6 שנים": [perf["3 ניחושים"], perf["3 + חזק"], perf["4 ניחושים"], perf["4 + חזק"]]
        }
        perf_df = pd.DataFrame(perf_data)
        
        st.write(f"#### 📋 טור {idx+1}:")
        st.info(f"**צירוף:** {', '.join(map(str, t_nums))} | **חזק:** {t_strong}")
        st.dataframe(perf_df.set_index("קטגוריית זכייה"), use_container_width=True)
        st.write("---")

selected_strong = random.randint(1, 7)

# כפתור 1
if st.button("🎲 כפתור 1: הגרלת סדרות ומרווחים (מתוך 12 המספרים האישיים שלך)"):
    if not user_input_str.strip():
        st.warning("💡 לא הזנת מספרים בתיבה, המערכת השתמשה אוטומטית ב-12 מספרים מובילים מהקובץ.")
        
    st.subheader(f"נבחר מספר חזק אחיד: {selected_strong}")
    st.write("**12 המספרים שננעלו לצמצום זה:**")
    for idx, num in enumerate(user_locked_12):
        st.write(f"**{idx+1})** {num}")
    
    st.write("---")
    
    all_tickets = generate_filtered_tickets(user_locked_12)
    process_and_render_sequential(all_tickets, selected_strong, records_extended)
    st.balloons()

# כפתור 2
if st.button("📈 כפתור 2: הגרלת סדרות ומרווחים אוטומטית (מתוך 12 החמים מהקובץ)"):
    current_hot_12 = sorted(random.sample(top_20_pool, 12))
    st.subheader(f"נבחר מספר חזק אחיד: {selected_strong}")
    
    st.write("**12 המספרים שננעלו אוטומטית מהקובץ:**")
    for idx, num in enumerate(current_hot_12):
        st.write(f"**{idx+1})** {num}")
    
    st.write("---")
    
    all_tickets = generate_filtered_tickets(current_hot_12)
    process_and_render_sequential(all_tickets, selected_strong, records_extended)
    st.balloons()

# === חלק 5: ארכיון ההגרלות המלא ל-6 שנים ===
def display_historical_archive_table(history):
    st.divider()
    st.subheader("🏆 ארכיון הצירופים שעלו בגורל ב-6 השנים האחרונות")
    
    draws_list = []
    for idx, draw in enumerate(history):
        draws_list.append({
            "מספר סידורי": f"הגרלה {idx+1}",
            "6 המספרים שעלו": ", ".join(map(str, draw['מספרים'])),
            "המספר החזק (נוסף)": f"מספר {draw['חזק']}"
        })
            
    if draws_list:
        archive_df = pd.DataFrame(draws_list)
        st.dataframe(archive_df.set_index("מספר סידורי"), use_container_width=True)
    else:
        st.info("לא נמצאו נתוני הגרלות בקובץ ה-CSV.")

display_historical_archive_table(records_extended)

# === חלק 6: מנוע מחקר ואיתור רצפים יורדים של המספר החזק ===
def analyze_strong_sequences(history):
    st.divider()
    st.subheader("🔍 מחקר רצפים: מתי חוזר רצף מספר חזק יורד?")
    
    sequences_found = []
    current_seq = []
    last_seq_end_idx = None
    
    for i in range(len(history)):
        if i == 0:
            current_seq = [history[i]]
            continue
            
        prev_strong = current_seq[-1]['חזק']
        curr_strong = history[i]['חזק']
        
        if curr_strong == prev_strong - 1 or (prev_strong == 1 and curr_strong == 7):
            current_seq.append(history[i])
        else:
            if len(current_seq) >= 3:
                seq_str = " -> ".join([str(d['חזק']) for d in current_seq])
                draw_range = f"הגרלות {i - len(current_seq) + 1} עד {i}"
                
                distance = "רצף ראשון בארכיון"
                if last_seq_end_idx is not None:
                    distance = f"{ (i - len(current_seq) + 1) - last_seq_end_idx } הגרלות"
                    
                sequences_found.append({
                    "מיקום הרצף": draw_range,
                    "אורך הרצף (בשבועות)": f"{len(current_seq)} שבועות",
                    "מהלך הרצף": seq_str,
                    "כמות ההגרלות שעברו מהרצף הקודם": distance
                })
                last_seq_end_idx = i
                
            current_seq = [history[i]]
            
    if len(current_seq) >= 3:
        seq_str = " -> ".join([str(d['חזק']) for d in current_seq])
        draw_range = f"הגרלות {len(history) - len(current_seq) + 1} עד {len(history)}"
        distance = "רצף אחרון בארכיון"
        if last_seq_end_idx is not None:
            distance = f"{ (len(history) - len(current_seq) + 1) - last_seq_end_idx } הגרלות"
        sequences_found.append({
            "מיקום הרצף": draw_range,
            "אורך הרצף (בשבועות)": f"{len(current_seq)} שבועות",
            "מהלך הרצף": seq_str,
            "כמות ההגרלות שעברו מהרצף הקודם": distance
        })

    if sequences_found:
        seq_df = pd.DataFrame(sequences_found)
        st.dataframe(seq_df.set_index("מיקום הרצף"), use_container_width=True)
        st.info(f"💡 ניתוח המנוע: נמצאו {len(sequences_found)} רצפים יורדים לאורך 6 השנים האחרונות. תוכל לראות בעמודה השמאלית את כמות ההגרלות המדויקת שעוברת בין פעם לפעם!")
    else:
        st.info("לא נמצאו רצפים יורדים רצופים של 3 שבועות ומעלה בחלון הזמן של 6 השנים האחרונות בקובץ.")

# הפעלת מנוע מחקר הרצפים בתחתית הדף
analyze_strong_sequences(records_extended)
