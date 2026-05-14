import streamlit as st
import pandas as pd
import requests
import io
from collections import Counter

# הגדרות כותרת לאפליקציה
st.set_page_config(page_title="מנחש הלוטו החכם", page_icon="🎰")
st.title("🎰 מחשב מספרי לוטו חמים")
st.write("המערכת שואבת נתונים ממפעל הפיס, מנתחת את השנה האחרונה ומבצעת צמצום ל-10 מספרים.")

def download_data():
    # כתובת להורדת נתוני לוטו (פורמט CSV/Excel של מפעל הפיס)
    url = "https://www.pais.co.il/Lotto/Pages/last_Results.aspx?download=1"
    try:
        response = requests.get(url)
        # שימוש ב-BytesIO לקריאת התוכן בזיכרון
        df = pd.read_excel(io.BytesIO(response.content))
        return df
    except Exception as e:
        st.error(f"שגיאה בהורדת הנתונים: {e}")
        return None

def analyze_logic(df):
    # שמות העמודות (יש לוודא התאמה לקובץ העדכני של מפעל הפיס)
    cols = ['מספר1', 'מספר2', 'מספר3', 'מספר4', 'מספר5', 'מספר6']
    
    # המרה לתאריכים וסינון שנה אחורה
    if 'תאריך_הגרלה' in df.columns:
        df['תאריך_הגרלה'] = pd.to_datetime(df['תאריך_הגרלה'])
        last_year = pd.Timestamp.now() - pd.DateOffset(years=1)
        df = df[df['תאריך_הגרלה'] > last_year]
    
    # חישוב שכיחות
    all_nums = df[cols].values.flatten()
    all_nums = [int(n) for n in all_nums if pd.notnull(n)]
    counts = Counter(all_nums)
    
    # 10 החמים ביותר
    hot_10 = [num for num, count in counts.most_common(10)]
    return sorted(hot_10)

def reduce_to_tables(hot_10):
    # אלגוריתם צמצום בסיסי ל-4 טבלאות
    h = hot_10
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
            hot_numbers = analyze_logic(data)
            
            st.subheader("🔥 10 המספרים החמים ביותר (שנה אחרונה)")
            st.write(", ".join(map(str, hot_numbers)))
            
            tables = reduce_to_tables(hot_numbers)
            
            st.subheader("📋 טבלאות מוצעות (צמצום)")
            for i, table in enumerate(tables, 1):
                st.info(f"**טבלה {i}:** {', '.join(map(str, sorted(table)))}")
            
            st.success("בהצלחה! זכור: הנתונים מבוססים על סטטיסטיקה בלבד.")
