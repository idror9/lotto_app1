import os
import random
import re
from collections import Counter
import pandas as pd
import streamlit as st

st.set_page_config(page_title="לוטו חכם", layout="centered")

st.markdown(
    """
    <style>
    html, body, [data-testid="stAppViewContainer"] { direction: RTL; text-align: right; }
    #MainMenu, footer, header { visibility: hidden; }
    .stButton>button { width: 100%; border-radius: 20px; height: 3.5em; font-weight: bold; }
    div[data-testid="stMarkdownContainer"] p, h1, h2, h3, h4, h5, h6 { text-align: right; direction: RTL; }
    div[data-testid="stSelectbox"] div[data-baseweb="select"] { direction: RTL; text-align: right; }
    div[data-testid="stDataFrame"] { direction: RTL; text-align: right; }
    </style>
    """,
    unsafe_allow_html=True,
)


def load_any_lotto_file():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = None
    for name in ["lotto2026.csv", "Lotto2026.csv", "lotto2026.CSV"]:
        test_path = os.path.join(current_dir, name)
        if os.path.exists(test_path):
            file_path = test_path
            break
    if file_path is None or not os.path.exists(file_path):
        return None
    try:
        with open(file_path, "r", encoding="utf-8-sig", errors="ignore") as f:
            content = f.read()
    except:
        return None

    records = []
    for line in content.split("\n"):
        tokens = re.findall(r"\b\d+\b", line)
        ints = [int(t) for t in tokens if 1 <= int(t) <= 37]
        if len(ints) >= 7:
            s_val = ints[-1] if 1 <= ints[-1] <= 7 else ints[0]
            series = ints[-7:-1] if 1 <= ints[-1] <= 7 else ints[1:7]
            if len(series) == 6 and 1 <= s_val <= 7:
                records.append({"מספרים": sorted(series), "חזק": s_val})
    return records


all_historical_records = load_any_lotto_file()
TOTAL_DRAWS = 624

if not all_historical_records:
    all_historical_records = []
    random.seed(random.randint(1, 10000))
    for _ in range(TOTAL_DRAWS):
        all_historical_records.append({
            "מספרים": sorted(random.sample(range(1, 38), 6)),
            "חזק": random.randint(1, 7),
        })
    is_sim = True
else:
    is_sim = False

records_extended = all_historical_records[:TOTAL_DRAWS]
if not is_sim:
    records_extended.reverse()

all_numbers, all_strong = [], []
for r in records_extended:
    all_numbers.extend(r["מספרים"])
    all_strong.append(r["חזק"])

counts = Counter(all_numbers)
strong_counts = Counter(all_strong)
top_20_pool = [n for n, c in counts.most_common(20)]
cold_numbers = [n for n in range(1, 38) if n not in top_20_pool][:7]

st.title("🎰 לוטו חכם - אנליזה מורחבת 6 שנים")
if is_sim:
    st.warning("⚠️ מציג נתוני סימולציה זמניים של 6 שנים.")
else:
    st.success(f"✔️ מנתח {len(records_extended)} הגרלות אמת מהקובץ.")

st.subheader("💰 ניתוח פיננסי: מספרים חזקים")
financial_data = []
for i in range(1, 8):
    total_i = sum(1 for r in records_extended if r.get("חזק") == i)
    power = (
        (strong_counts.get(i, 0) / len(records_extended) * 100)
        if records_extended
        else 0
    )
    financial_data.append({
        "מספר חזק": f"מספר {i}",
        "הופעות ב-6 שנים": f"{total_i} פעמים",
        "מדד עוצמה": f"{power:.1f}%",
        "מיון": power,
    })
f_df = (
    pd.DataFrame(financial_data)
    .sort_values(by="מיון", ascending=False)
    .drop(columns=["מיון"])
)
st.dataframe(f_df.set_index("מספר חזק"), use_container_width=True)

st.divider()

st.subheader("🔮 בדיקת סיכוי למספר החזק הבא")
chosen_strong = st.selectbox(
    "בחר את המספר החזק האחרון שיצא:", options=list(range(1, 8)), index=5
)
next_list = []
for i in range(len(records_extended) - 1):
    if records_extended[i].get("חזק") == chosen_strong:
        if records_extended[i + 1].get("חזק"):
            next_list.append(records_extended[i + 1]["חזק"])
counts_next = Counter(next_list)

if next_list:
    stats_data = []
    for i in range(1, 8):
        times = counts_next.get(i, 0)
        chance = (times / len(next_list)) * 100
        stats_data.append({
            "המספר הבא": f"מספר {i}",
            "הופעות": f"{times} פעמים",
            "סיכוי": f"{chance:.1f}%",
            "מיון": chance,
        })
    s_df = (
        pd.DataFrame(stats_data)
        .sort_values(by="מיון", ascending=False)
        .drop(columns=["מיון"])
    )
    st.dataframe(s_df.set_index("המספר הבא"), use_container_width=True)
else:
    st.info("לא נמצאו מספיק נתונים.")

st.divider()

st.subheader("✍️ הזנת 12 מספרים אישיים לצמצום")
user_input_str = st.text_input("הקש 12 מספרים מופרדים בפסיקים:", value="")
user_locked_12 = list(
    set([
        int(n)
        for n in re.findall(r"\b\d+\b", user_input_str)
        if 1 <= int(n) <= 37
    ])
)
while len(user_locked_12) < 12:
    for num in top_20_pool:
        if num not in user_locked_12:
            user_locked_12.append(num)
        if len(user_locked_12) == 12:
            break
user_locked_12 = sorted(user_locked_12[:12])


def generate_filtered_tickets(pool_12):
    tickets = []
    for _ in range(8):
        valid = False
        attempts = 0
        table = []
        while not valid and attempts < 200:
            table = sorted(random.sample(pool_12, 6))
            diffs = [table[j + 1] - table[j] for j in range(5)]
            cond_diff = any(d in [1, 2, 3] for d in diffs)
            evens = sum(1 for n in table if n % 2 == 0)
            cond_balance = evens in [2, 3, 4]
            cond_high = any(n > 31 for n in table)
            if cond_diff and cond_balance and cond_high:
                valid = True
            attempts += 1
        if not valid:
            table = sorted(random.sample(pool_12, 6))
        tickets.append(table)
    return tickets


# מחולל מיוחד המתחשב בכל תכונות הגרלות הענק (מעל 20 מיליון)
def generate_jackpot_tickets():
    tickets = []
    for _ in range(8):
        valid = False
        attempts = 0
        table = []
        while not valid and attempts < 500:
            table = sorted(random.sample(range(1, 38), 6))

            # 1. סכום כולל בטווח 100 עד 140
            total_sum = sum(table)
            if not (100 <= total_sum <= 140):
                attempts += 1
                continue

            # 2. איזון זוגי / אי-זוגי (2, 3, או 4 זוגיים)
            evens = sum(1 for n in table if n % 2 == 0)
            if evens not in [2, 3, 4]:
                attempts += 1
                continue

            # 3. פריסת עשרות: לפחות 1 מ-(1-9) ולפחות 2 מ-(20-29)
            d_1_9 = sum(1 for n in table if 1 <= n <= 9)
            d_20_29 = sum(1 for n in table if 20 <= n <= 29)
            if d_1_9 < 1 or d_20_29 < 2:
                attempts += 1
                continue

            # 4. מניעת 3 מספרים עוקבים ברצף
            has_triple = any(
                table[j] + 1 == table[j + 1] and table[j + 1] + 1 == table[j + 2]
                for j in range(len(table) - 2)
            )
            if has_triple:
                attempts += 1
                continue

            valid = True

        if not valid:
            table = sorted(random.sample(range(1, 38), 6))
        tickets.append(table)
    return tickets


def render_tickets_perf(tickets, t_strong, history):
    st.write("### 🎫 8 הטורים המומלצים למילוי:")
    rows = [
        {
            "טור": f"טור {i+1}",
            "צירוף": ", ".join(map(str, t)),
            "חזק": f"מספר {t_strong}",
        }
        for i, t in enumerate(tickets)
    ]
    st.dataframe(pd.DataFrame(rows).set_index("טור"), use_container_width=True)

    st.write("### 📊 ביצועים היסטוריים ב-6 שנים:")
    for i, t in enumerate(tickets):
        sum_3, sum_3s, sum_4, sum_4s = 0, 0, 0, 0
        for draw in history:
            m = len(set(t) & set(draw["מספרים"]))
            sm = t_strong == draw["חזק"]
            if m == 3 and not sm:
                sum_3 += 1
            elif m == 3 and sm:
                sum_3s += 1
            elif m == 4 and not sm:
                sum_4 += 1
            elif m == 4 and sm:
                sum_4s += 1
        perf_df = pd.DataFrame({
            "קטגוריה": ["3 ניחושים", "3 + חזק", "4 ניחושים", "4 + חזק"],
            "הצלחות": [sum_3, sum_3s, sum_4, sum_4s],
        })
        st.write(
            f"📋 **טור {i+1}:** {', '.join(map(str, t))} | חזק: {t_strong}"
        )
        st.dataframe(
            perf_df.set_index("קטגוריה"), use_container_width=True
        )


selected_strong = random.randint(1, 7)

if st.button("🎲 כפתור 1: הגרלה מהמספרים האישיים שלך"):
    st.subheader(f"חזק אחיד שנבחר: {selected_strong}")
    render_tickets_perf(
        generate_filtered_tickets(user_locked_12),
        selected_strong,
        records_extended,
    )

if st.button("📈 כפתור 2: הגרלה אוטומטית מ-12 החמים ביותר"):
    st.subheader(f"חזק אחיד שנבחר: {selected_strong}")
    render_tickets_perf(
        generate_filtered_tickets(sorted(random.sample(top_20_pool, 12))),
        selected_strong,
        records_extended,
    )

recent_10 = (
    records_extended[-10:]
    if len(records_extended) >= 10
    else records_extended
)
r_nums = []
for d in recent_10:
    r_nums.extend(d["מספרים"])
rec_pool = [n for n, c in Counter(r_nums).most_common(12)]

if st.button("🔮 כפתור 3: הפקת 12 מספרים חמים מבוססי תופעות"):
    l1 = random.sample(rec_pool, min(5, len(rec_pool))) if rec_pool else []
    l2 = random.sample(top_20_pool, 5)
    l3 = random.sample(cold_numbers, 2)

    g_12 = sorted(list(set(l1 + l2 + l3)))
    while len(g_12) < 12:
        for num in top_20_pool:
            if num not in g_12:
                g_12.append(num)
            if len(g_12) == 12:
                break
    g_12.sort()

    st.subheader(f"חזק אחיד שנבחר: {selected_strong}")
    st.write("### 🔥 בריכת 12 מספרים אופטימלית משתנה (רענון אוטומטי):")
    st.code(
        f"🎯 12 המספרים שנבחרו עבורך: {', '.join(map(str, g_12))}",
        language="text",
    )
    render_tickets_perf(
        generate_filtered_tickets(g_12), selected_strong, records_extended
    )

# כפתור 4: מחולל שילובים מבוסס תכונות הגרלות ענק (מעל 20 מיליון)
jackpot_strong = random.choice([3, 4, 5, 3, 4, 5, 2, 6])
if st.button("🏆 כפתור 4: מחולל שילובים מבוסס הגרלות ענק (מעל 20 מיליון)"):
    st.subheader(f"חזק מומלץ להגרלות ענק: {jackpot_strong}")
    st.info(
        "💡 טורים אלו נבנו לפי תכונות הזכייה: סכום כולל (100-140), פיזור עשרות, איזון זוגי/אי-זוגי וללא רצפים משולשים."
    )
    jackpot_tickets = generate_jackpot_tickets()
    render_tickets_perf(jackpot_tickets, jackpot_strong, records_extended)

st.divider()

st.subheader("🏆 ארכיון ומחקר רצפים יורדים")
with st.expander("🔍 לחץ כאן לצפייה במחקר הרצפים וזמני המחזור"):
    seq_found, current_seq, last_idx = [], [], None
    for i in range(len(records_extended)):
        if i == 0:
            current_seq = [records_extended[i]]
            continue
        p_s, c_s = current_seq[-1]["חזק"], records_extended[i]["חזק"]
        if c_s == p_s - 1 or (p_s == 1 and c_s == 7):
            current_seq.append(records_extended[i])
        else:
            if len(current_seq) >= 3:
                dist = (
                    "רצף ראשון"
                    if last_idx is None
                    else f"{i - len(current_seq) - last_idx} הגרלות"
                )
                seq_found.append({
                    "מיקום": f"הגרלות {i-len(current_seq)} עד {i}",
                    "אורך": f"{len(current_seq)} שבועות",
                    "מהלך": " -> ".join([
                        str(d["חזק"]) for d in current_seq
                    ]),
                    "זמן מחזור": dist,
                })
                last_idx = i
            current_seq = [records_extended[i]]
    if seq_found:
        st.dataframe(
            pd.DataFrame(seq_found).set_index("מיקום"),
            use_container_width=True,
        )

st.subheader("⚡ מנוע סריקה מהירה והמלצות אוטומטיות")
if len(records_extended) >= 2:
    last_d, prev_d = records_extended[-1], records_extended[-2]
    all_r10, s_r10, ev_c, c_c = [], [], 0, 0
    for d in recent_10:
        all_r10.extend(d["מספרים"])
        s_r10.append(d["חזק"])
        ev_c += sum(1 for n in d["מספרים"] if n % 2 == 0)
        for j in range(len(d["מספרים"]) - 1):
            if d["מספרים"][j + 1] - d["מספרים"][j] == 1:
                c_c += 1

    mag_nums = [
        num for num, count in Counter(all_r10).items() if count >= 3
    ]
    top_s10, c_s10 = Counter(s_r10).most_common(1)[0]
    pct_ev = (ev_c / (len(recent_10) * 6)) * 100

    st.write(
        f"🎯 **חזק שולט ב-10 האחרונות:** מספר {top_s10} (עלה {c_s10} פעמים)."
    )
    st.write(
        f"📊 **מדד דחיסות ואיזון:** {c_c} מקרים עוקבים | {pct_ev:.1f}% זוגיים."
    )

    cond_down_1 = last_d["חזק"] == prev_d["חזק"] - 1
    cond_down_2 = prev_d["חזק"] == 1 and last_d["חזק"] == 7
    cond_up_1 = last_d["חזק"] == prev_d["חזק"] + 1
    cond_up_2 = prev_d["חזק"] == 7 and last_d["חזק"] == 1

    s_rec = [last_d["חזק"] - 1 if last_d["חזק"] > 1 else 7]
    if cond_down_1 or cond_down_2:
        s_rec = [
            last_d["חזק"] - 1 if last_d["חזק"] > 1 else 7,
            7 if last_d["חזק"] - 1 == 1 else last_d["חזק"],
        ]

    sticky = list(set(last_d["מספרים"]) & set(prev_d["מספרים"]))
    r_rec = sticky if sticky else (mag_nums[:3] if mag_nums else [12, 24, 25])

    st.write("### 💡 המלצות המנוע להגרלה הקרובה:")
    st.code(
        f"🔮 מספרים חזקים מומלצים: {', '.join(map(str, s_rec))}",
        language="text",
    )
    st.code(
        f"🎰 מספרים רגילים לשילוב: {', '.join(map(str, sorted(list(set(r_rec)))))}",
        language="text",
    )
