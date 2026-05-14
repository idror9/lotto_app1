import streamlit as st
import pandas as pd
import requests
import io
from collections import Counter

st.set_page_config(page_title="מנחש הלוטו החכם", page_icon="🎰")
st.title("🎰 מחשב מספרי לוטו חמים")

def download_data():
    # כתובת חלופית וישירה יותר לקובץ
    url = "https://www.pais.co.il/Lotto/Pages/last_Results.aspx?download=1"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36',
        'Accept': 'application/vnd.ms-excel,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet, */*'
    }
    
    try:
        # יצירת Session כדי לשמור על עוגיות (זה עוזר לעקוף חסימות)
        session = requests.Session()
        response = session.get(url, headers=headers, timeout=15)
        
        # אם השרת חוסם, ננסה כתובת ישירה נוספת
        if b'<html' in response.content.lower() or response.status_code != 200:
            direct_url = "https://www.pais.co.il/Lotto/_layouts/15/PAIS.ListCreators/Handler/LottoResultsHandler.ashx?ListID=8e063d89-9b48-4389-9a25-f1262d590472&Mode=Download"
            response = session.get(direct_url, headers=headers, timeout=15)

        if b'<html' in response.content.lower():
            st.error("האתר של מפעל הפיס חוסם גישה אוטומטית כרגע. נסה שוב בעוד כמה דקות.")
            return None
            
        # ניסיון קריאה עם מנועים שונים
        try:
            return pd.read_excel(io.BytesIO(response.content), engine='openpyxl')
        except:
            return pd.read_excel(io.BytesIO(response.content), engine='xlrd')
            
    except Exception as e:
        st.error(f"שגיאה טכנית: {e}")
        return None

def analyze_logic(df):
    # ניקוי עמודות
    df.columns = [str(col).strip() for col in df.columns]
    
    # חיפוש עמודות לפי מילות מפתח (גמישות למקרה שהשם משתנה)
    lotto_cols = [col for col in df.columns if 'מספר' in col and any(char.isdigit() for char in col)][:6]
    strong_col = [col for col in df.columns if 'חזק' in col]
    date_col = [col for col in df.columns if 'תאריך' in col]

    if not lotto_cols:
        st.warning("לא הצלחתי לזהות את עמודות המספרים בקובץ.")
        return [], "לא נמצא"

    # סינון שנה אחורה
    if date_col:
        df[date_col[0]] = pd.to_datetime(df[date_col[0]], dayfirst=True, errors='coerce')
        df = df.dropna(subset=[date_col[0]])
        last_year = pd.Timestamp.now() - pd.DateOffset(years=1)
        df = df[df[date_col[0]] > last_year]
    
    # חישוב מספרים חמים
    all_nums = df[lotto_cols].values.flatten()
    all_nums = [int(n) for n in all_nums if pd.notnull(n) and str(n).replace('.0','').isdigit()]
    hot_10 = [num for num, count in Counter(all_nums).most_common(10)]
    
    # מספר חזק
    hot_strong = "לא נמצא"
    if strong_col:
        strong_nums = [int(n) for n in df[strong_col[0]].values if pd.notnull(n) and str(n).replace('.0','').isdigit()]
        if strong_nums:
            hot_strong = Counter(strong_nums).most_common(1)[0][0]

    return sorted(hot_10), hot_strong

# ממשק משתמש
if st.button("בצע ניתוח נתונים"):
    with st.spinner('מתחבר לשרת מפעל הפיס...'):
        data = download_data()
        if data is not None:
            hot_numbers, hot_strong = analyze_logic(data)
            if hot_numbers:
                st.success("הנתונים נותחו בהצלחה!")
                st.write(f"**10 החמים:** {', '.join(map(str, hot_numbers))}")
                st.write(f"**חזק מומלץ:** {hot_strong}")
                
                # תצוגת טבלאות צמצום
                st.divider()
                st.subheader("📋 טבלאות לצילום (צמצום)")
                h = hot_numbers
                tables = [[h[0],h[1],h[2],h[3],h[4],h[5]], [h[4],h[5],h[6],h[7],h[8],h[9]], [h[0],h[2],h[4],h[6],h[8],h[9]]]
                for i, t in enumerate(tables, 1):
                    st.info(f"טבלה {i}: {sorted(t)}")
