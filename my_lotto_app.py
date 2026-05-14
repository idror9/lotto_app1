import streamlit as st
import pandas as pd
import requests
import io
from collections import Counter

# הגדרות כותרת לאפליקציה
st.set_page_config(page_title="מנחש הלוטו החכם", page_icon="🎰")
st.title("🎰 מחשב מספרי לוטו חמים")
st.write("המערכת שואבת נתונים ממפעל הפיס, מנתחת את השנה האחרונה ומבצעת צמצום.")

def download_data():
    # כתובת להורדת נתוני לוטו (קובץ אקסל של מפעל הפיס)
    url = "https://www.pais.co.il/Lotto/Pages/last_Results.aspx?download=1"
    try:
        response = requests.get(url)
        response.raise_for_status()
        # שימוש במנוע openpyxl כדי למנוע שגיאות פורמט
        df = pd.read_excel(io.BytesIO(response.content), engine='openpyxl')
        return df
    except Exception as e:
        st.error(f"שגיאה בהורדת הנתונים: {e}")
        return None

def analyze_logic(df):
    # ניקוי שמות עמודות (הסרת רווחים מיותרים אם יש)
    df.columns = [col.strip() for col in df.columns]
    
    # זיהוי עמודות המספרים (1-6) והמספר החזק
    # הערה: שמות העמודות המקוריים באתר הם לרוב 'מספר1', 'מספר2' וכו'
    lotto_cols = ['מספר1', 'מספר2', 'מספר3', 'מספר4', 'מספר5', 'מספר6']
    strong_col = 'המספר החזק'
    date_col = 'תאריך הגרלה'

    # המרה לתאריכים וסינון שנה אחורה
    if date_col in df.columns:
        df[date_col] = pd.to_datetime(df[date_col], dayfirst=True)
        last_year = pd.Timestamp.now() - pd.DateOffset(years=1)
        df = df[df[date_col] > last_year]
    
    # חישוב שכיחות למספרים הרגילים
    all_nums = df[lotto_cols].values.flatten()
    all_nums = [int(n) for n in all_nums if pd.notnull(n)]
    counts = Counter(all_nums)
    hot_10 = [num for num, count in counts.most_common(10)]
    
    # חישוב המספר החזק הכי נפוץ
    if strong_col in df.columns:
        strong_nums = [int(n) for n in df[strong_col].values if pd.notnull(n)]
        hot_strong = Counter(strong_nums).most_common(1)[0][0]
    else:
        hot_strong = "לא נמצא"

    return sorted(hot_10), hot_strong

def reduce_to_tables(hot_10):
    # אלגוריתם צמצום בסיסי ל-4 טבלאות
    h = hot_10
    if len(h) < 10:
        return []
    tables = [
        [h[0], h[1], h[2], h[3], h[4], h[5]],
        [h[4], h[5], h[6], h[7], h[8], h[9]],
        [h[0], h[2], h[4], h[6], h[8], h[9]],
        [h[1], h[3], h[5], h[7], h[8], h[9]]
    ]
    return tables

# כפתור הפעלה
if st.button("חשב מספרים חמים וצמצם"):
    with st.spinner('מושך נתונים ומנתח...'):
        data = download_data()
        if data is not None:
            hot_numbers, hot_strong = analyze_logic(data)
            
            st.subheader("🔥 10 המספרים החמים ביותר (שנה אחרונה)")
            st.write(", ".join(map(str, hot_numbers)))
            
            st.subheader("🎯 המספר החזק הכי חם")
            st.success(f"המספר החזק המומלץ: {hot_strong}")
            
            tables = reduce_to_tables(hot_numbers)
            
            st.subheader("📋 טבלאות מוצעות (צמצום)")
            if tables:
                for i, table in enumerate(tables, 1):
                    st.info(f"**טבלה {i}:** {', '.join(map(str, sorted(table)))}")
            else:
                st.warning("אין מספיק נתונים לביצוע צמצום.")
            
            st.caption("הנתונים נשאבו בזמן אמת מאתר מפעל הפיס.")
