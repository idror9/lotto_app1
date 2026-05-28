import streamlit as st
import pandas as pd
from collections import Counter
import random
import os
import re

# הגדרת דף נקייה והסתרת תפריטים מיותרים לנייד
st.set_page_config(page_title="לוטו חכם - גרסה יציבה", layout="centered")

# קוד עיצוב ליישור מוחלט מימין לשמאל (RTL), התאמה לנייד ושינוי רקע התיבות ללבן
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
    
    /* שינוי הרקע של תיבות הטורים ללבן עם מסגרת ברורה */
    .ticket-box {
        background-color: #ffffff;
        border: 2px solid #b9bdc5;
        border-right: 6px solid #ff4b4b;
        padding: 12px;
        margin: 8px 0px;
        border-radius: 0px 10px 10px 0px;
        font-weight: bold;
        color: #000000;
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
            'חזק
