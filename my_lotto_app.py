import streamlit as st
import pandas as pd
from collections import Counter
import random
import os

st.set_page_config(page_title="לוטו חכם - אבחון", layout="centered")

# בדיקה אילו קבצים קיימים בשרת
st.write("### 📂 בדיקת סביבת העבודה בשרת:")
try:
    current_files = os.listdir('.')
    st.write("הקבצים שנמצאו בתיקייה הראשית:")
    st.code(", ".join(current_files))
except Exception as e:
    st.error(f"שגיאה בסריקת התיקייה: {e}")

@st.cache_data
def load_mifal_hapais_data(file_path):
    encodings = ['utf-8', 'windows-1255', 'ansi', 'utf-8-sig']
    for enc in encodings:
        try:
            df = pd.read_csv(file_path, encoding=enc, sep=None, engine='python')
            df.columns = df.columns.str.strip().str.replace('\ufeff', '')
            strong_col = [col for col in df.columns if 'חזק' in col or 'Strong' in col]
            num_cols = [col for col in df.columns if ('מספר' in col or 'Num' in col) and col != strong_col[0]]
            num_cols = sorted(num_cols)[:6]
            
            records = []
            for _, row in df.iterrows():
                try:
                    nums = [int(row[c]) for c in num_cols if pd.notna(row[c])]
                    strong = int(row[strong_col[0]]) if pd.notna(row[strong_col[0]]) else None
                    if len(nums) == 6 and strong is not None:
                        records.append({'מספרים': nums, 'חזק': strong})
                except:
                    continue
            if records:
                return records, None
        except Exception as e:
            last_error = str(e)
            continue
    return None, f"הקובץ נמצא אך נכשל בפענוח. שגיאה אחרונה: {last_error}" if 'last_error' in locals() else "לא ניתן לקרוא את הקובץ"

# ניסיון טעינה
all_records, error_msg = load_mifal_hapais_data('lotto2026.csv')

if all_records:
    st.success(f"🎉 הצלחה! נטענו {len(all_records)} הגרלות.")
    # הצגת טבלה בסיסית זמנית כדי לראות שהכל עובד
    st.write(all_records[:5])
else:
    st.error("🚨 קובץ הנתונים לא נטען.")
    if error_msg:
        st.info(error_msg)
