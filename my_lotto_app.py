import streamlit as st
import pandas as pd
import requests
import io

st.set_page_config(page_title="היסטוריית זכיות לוטו", page_icon="📈")
st.title("📈 היסטוריית הגרלות וזכיות")

def get_history():
    # כתובת ישירה לקובץ היסטוריה (CSV) שהוא קל יותר להורדה
    url = "https://www.pais.co.il/Lotto/Pages/last_Results.aspx?download=1&type=csv"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        # אם האתר חוסם, נשתמש בנתונים לדוגמה כדי שהאפליקציה לא תהיה ריקה
        if response.status_code != 200 or b'<html' in response.content.lower():
            return None
        
        df = pd.read_csv(io.BytesIO(response.content))
        return df
    except:
        return None

# כפתור רענון
if st.button("טען היסטוריית זכיות"):
    with st.spinner('מושך נתונים מהארכיון...'):
        df = get_history()
        
        if df is not None:
            # ניקוי עמודות
            df.columns = [str(col).strip() for col in df.columns]
            
            # הצגת הנתונים בטבלה יפה
            st.subheader("תוצאות הגרלות אחרונות")
            
            # בחירת עמודות רלוונטיות להצגה
            cols_to_show = [c for c in df.columns if any(x in c for x in ['תאריך', 'מספר', 'חזק'])]
            st.dataframe(df[cols_to_show].head(20)) # מציג את 20 ההגרלות האחרונות
            
            st.success("הנתונים עודכנו בהצלחה!")
        else:
            st.error("לא ניתן למשוך נתונים אוטומטית מאתר מפעל הפיס עקב חסימה.")
            st.info("""
            **אפשרות חלופית:**
            מכיוון שהאתר חוסם את השרת, תוכל להוריד את הקובץ ידנית מהקישור למטה ולהעלות אותו כאן כדי לראות את ההיסטוריה שלך:
            """)
            st.markdown("[הורד קובץ היסטוריה מכאן](https://www.pais.co.il/Lotto/Pages/last_Results.aspx?download=1)")

# אפשרות העלאה ידנית (למקרה שהאוטומטי נחסם)
uploaded_file = st.file_uploader("או העלה קובץ אקסל/CSV ששמור אצלך:", type=["xlsx", "csv"])
if uploaded_file:
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)
    
    st.subheader("היסטוריית זכיות מהקובץ שלך:")
    st.dataframe(df.head(50)) # מציג את 50 השורות הראשונות
