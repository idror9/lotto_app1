import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="היסטוריית לוטו ממשלתית", page_icon="📈", layout="wide")
st.title("📈 היסטוריית הגרלות לוטו - נתונים רשמיים")

def get_gov_data():
    # שליפת נתונים ממאגר המידע הממשלתי הפתוח (חסין חסימות)
    # זהו משאב של נתוני הגרלות הלוטו
    resource_id = "f0067677-7440-4545-9372-b7b5c822e039" 
    url = f"https://data.gov.il/api/3/action/datastore_search?resource_id={resource_id}&limit=1000"
    
    try:
        response = requests.get(url, timeout=15)
        if response.status_code == 200:
            data = response.json()
            records = data['result']['records']
            df = pd.DataFrame(records)
            return df
        return None
    except Exception as e:
        st.error(f"שגיאה בחיבור למאגר הממשלתי: {e}")
        return None

if st.button("טען היסטוריית הגרלות ממאגר הממשלה"):
    with st.spinner('מתחבר למאגר הנתונים הממשלתי...'):
        df = get_gov_data()
        
        if df is not None and not df.empty:
            st.success("הנתונים נמשכו בהצלחה ממאגר data.gov.il")
            
            # ניקוי וסידור הטבלה
            # שמות העמודות במאגר הממשלתי עשויים להיות באנגלית או שונים במעט
            st.subheader("20 ההגרלות האחרונות")
            st.dataframe(df.head(20), use_container_width=True)
            
            # אפשרות להורדת הקובץ שנוצר מהמאגר
            csv = df.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                label="הורד את ההיסטוריה כקובץ CSV לטלפון",
                data=csv,
                file_name="lotto_history_gov.csv",
                mime="text/csv",
            )
        else:
            st.error("לא הצלחתי למשוך נתונים. המאגר הממשלתי לא זמין כרגע.")

st.divider()
st.write("### אפשרות ב': העלאה ידנית")
uploaded_file = st.file_uploader("אם יש לך קובץ אקסל או CSV, העלה אותו כאן:", type=["xlsx", "csv", "xls"])

if uploaded_file:
    try:
        if uploaded_file.name.endswith('.csv'):
            df_manual = pd.read_csv(uploaded_file)
        else:
            df_manual = pd.read_excel(uploaded_file)
        st.subheader("נתונים מהקובץ שהעלית:")
        st.dataframe(df_manual)
    except Exception as e:
        st.error(f"שגיאה בקריאת הקובץ: {e}")
