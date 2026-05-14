import streamlit as st
import pandas as pd
import requests
import io
from collections import Counter

st.set_page_config(page_title="מנחש הלוטו החכם", page_icon="🎰")
st.title("🎰 מחשב מספרי לוטו חמים")
st.write("המערכת שואבת נתונים ממפעל הפיס, מנתחת את השנה האחרונה ומבצעת צמצום.")

def download_data():
    # כתובת ישירה לקובץ האקסל
    url = "https://www.pais.co.il/Lotto/Pages/last_Results.aspx?download=1"
    
    # הוספת Headers כדי לדמות דפדפן אמיתי (מונע חסימות)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        # בדיקה אם התוכן שהתקבל הוא HTML במקום אקסל
        if b'<html' in response.content.lower():
            st.error("האתר החזיר דף אינטרנט במקום קובץ נתונים. ייתכן שיש חסימה זמנית או שינוי בכתובת.")
            return None
            
        # ניסיון קריאה כ-Excel
        try:
            # מנסה לקרוא בפורמט המודרני
            df = pd.read_excel(io.BytesIO(response.content), engine='openpyxl')
        except:
            # אם נכשל, מנסה כפורמט ישן (xls)
            df = pd.read_excel(io.BytesIO(response.content))
            
        return df
    except Exception as e:
        st.error(f"שגיאה בהורדת הנתונים: {e}")
        return None

def analyze_logic(df):
    # ניקוי שמות עמודות מרווחים
    df.columns = [str(col).strip() for col in df.columns]
    
    # הגדרת שמות העמודות כפי שהם מופיעים לרוב בקובץ של הפיס
    lotto_cols = ['מספר1', 'מספר2', 'מספר3', 'מספר4', 'מספר5', 'מספר6']
    strong_col = 'המספר החזק'
    date_col = 'תאריך הגרלה'

    # המרה לתאריכים וסינון שנה אחורה
    if date_col in df.columns:
        df[date_col] = pd.to_datetime(df[date_col], dayfirst=True, errors='coerce')
        df = df.dropna(subset=[date_col])
        last_year = pd.Timestamp.now() - pd.DateOffset(years=1)
        df = df[df[date_col] > last_year]
    
    # וידוא שעמודות המספרים קיימות
    available_cols = [c for c in lotto_cols if c in df.columns]
    if not available_cols:
        st.error(f"לא נמצאו עמודות מספרים. עמודות קיימות: {list(df.columns)}")
        return [], "לא נמצא"

    all_nums = df[available_cols].values.flatten()
    all_nums = [int(n) for n in all_nums if pd.notnull(n) and str(n).isdigit()]
    counts = Counter(all_nums)
    hot_10 = [num for num, count in counts.most_common(10)]
    
    hot_strong = "לא נמצא"
    if strong_col in df.columns:
        strong_nums = [int(n) for n in df[strong_col].values if pd.notnull(n) and str(n).isdigit()]
        if strong_nums:
            hot_strong = Counter(strong_nums).most_common(1)[0][0]

    return sorted(hot_10), hot_strong

def reduce_to_tables(hot_10):
    if len(hot_10) < 10: return []
    h = hot_10
    return [
        [h[0], h[1], h[2], h[3], h[4], h[5]],
        [h[4], h[5], h[6], h[7], h[8], h[9]],
        [h[0], h[2], h[4], h[6], h[8], h[9]],
        [h[1], h[3], h[5], h[7], h[8], h[9]]
    ]

if st.button("חשב מספרים חמים וצמצם"):
    with st.spinner('מושך נתונים ומנתח...'):
        data = download_data()
        if data is not None:
            hot_numbers, hot_strong = analyze_logic(data)
            
            if hot_numbers:
                st.subheader("🔥 10 המספרים החמים ביותר (שנה אחרונה)")
                st.write(", ".join(map(str, hot_numbers)))
                
                st.subheader("🎯 המספר החזק הכי חם")
                st.success(f"המספר החזק המומלץ: {hot_strong}")
                
                tables = reduce_to_tables(hot_numbers)
                st.subheader("📋 טבלאות מוצעות (צמצום)")
                for i, table in enumerate(tables, 1):
                    st.info(f"**טבלה {i}:** {', '.join(map(str, sorted(table)))}")
            else:
                st.warning("לא נמצאו נתונים מתאימים לניתוח.")
