import streamlit as st
import pandas as pd
import re
import requests

# הגדרות עמוד
st.set_page_config(page_title="הספריה שלי", page_icon="📚", layout="centered")

# קישור ל-Google Apps Script ששלחת
SCRIPT_URL = "https://script.google.com/macros/s/AKfycbzSUXAJj3Diw9uth4J6z9P40xg7w4G0ny1zQKXKIky25IY3GIBlVdk9LEGRAtNkj9pvtQ/exec"

# פונקציית עזר להדגשת טקסט
def highlight_search(text, query):
    if not query or not text: return text
    pattern = re.compile(f"({re.escape(query)})", re.IGNORECASE)
    return pattern.sub(r'<mark style="background-color: yellow; padding: 0 2px;">\1</mark>', str(text))

# טעינת נתונים מגוגל שיטס
@st.cache_data(ttl=60)
def load_live_data():
    sheet_id = "14v7PSy9fKCMVvTvFHdx5ECrwcmrnRok2S5luvfC0O7Q"
    gid = "1314151533"
    csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"
    try:
        df = pd.read_csv(csv_url)
        df = df.dropna(how='all').fillna("")
        df.columns = df.columns.str.strip()
        return df
    except Exception as e:
        st.error(f"שגיאה בחיבור לגוגל שיטס: {e}")
        return None

# ניהול מצב האפליקציה
if 'items_to_show' not in st.session_state:
    st.session_state.items_to_show = 5
if 'last_search' not in st.session_state:
    st.session_state.last_search = ""

df = load_live_data()

# יצירת טאבים (לשוניות) למראה נקי בטלפון
tab1, tab2 = st.tabs(["🔍 חיפוש ספר", "➕ הוספת ספר"])

with tab1:
    st.title("חיפוש בספריה")
    search = st.text_input("חפש שם ספר, סופר, סדרה או עולם:", placeholder="למשל: דלמטים...")

    if search != st.session_state.last_search:
        st.session_state.items_to_show = 5
        st.session_state.last_search = search

    if search:
        search_columns = ['שם הספר', 'סופר', 'שם הסדרה', 'עולם']
        existing_cols = [col for col in search_columns if col in df.columns]
        mask = df[existing_cols].apply(lambda row: row.astype(str).str.contains(search, case=False).any(), axis=1)
        results = df[mask]

        if not results.empty:
            total_results = len(results)
            st.write(f"נמצאו **{total_results}** תוצאות:")
            
            shown_results = results.head(st.session_state.items_to_show)
            for _, row in shown_results.iterrows():
                book_name = highlight_search(row.get('שם הספר', ''), search)
                author = highlight_search(row.get('סופר', ''), search)
                series = highlight_search(row.get('שם הסדרה', ''), search)
                world = highlight_search(row.get('עולם', ''), search)
                location = row.get('מיקום_', 'לא צוין')
                
                card_html = (
                    f'<div style="border: 1px solid #ddd; padding: 15px; border-radius: 8px; '
                    f'margin-bottom: 10px; background-color: white; direction: rtl; text-align: right;">'
                    f'<div style="font-size: 1.15em; font-weight: bold; margin-bottom: 5px; color: #1e1e1e;">{book_name}</div>'
                    f'<div style="color: #444;">✍️ {author}</div>'
                    f'<div style="font-size: 0.85em; color: #666; margin-top: 5px;">'
                    f'{"📖 סדרה: " + series if row.get("שם הסדרה") else ""} '
                    f'{" | 🌍 עולם: " + world if row.get("עולם") else ""}</div>'
                    f'<div style="margin-top: 10px; color: #d32f2f; font-weight: bold;">📍 מיקום: {location}</div>'
                    f'</div>'
                )
                st.markdown(card_html, unsafe_allow_html=True)

            if st.session_state.items_to_show < total_results:
                if st.button(f"הצג עוד תוצאות ({total_results - st.session_state.items_to_show} נותרו)..."):
                    st.session_state.items_to_show += 5
                    st.rerun()
        else:
            st.warning(f"המילה '{search}' לא נמצאה.")
    else:
        st.info(f"בספריה יש {len(df)} ספרים רשומים.")
        if st.button("🔄 רענן נתונים מהשיטס"):
            st.cache_data.clear()
            st.rerun()

with tab2:
    st.title("הוספת ספר חדש")
    st.write("מלא את פרטי הספר והוא יתווסף ישירות לגוגל שיטס שלך.")
    
    with st.form("new_book_form", clear_on_submit=True):
        f_title = st.text_input("שם הספר*")
        f_author = st.text_input("סופר*")
        f_series = st.text_input("שם הסדרה")
        f_series_num = st.text_input("מספר בסדרה")
        f_world = st.text_input("עולם")
        f_location = st.text_input("מיקום (למשל: סלון מדף א)*")
        f_publisher = st.text_input("הוצאה")
        f_year = st.text_input("שנת הוצאה")
        
        submitted = st.form_submit_button("➕ שמור לספריה")
        
        if submitted:
            if not f_title or not f_author or not f_location:
                st.error("חובה למלא שם ספר, סופר ומיקום!")
            else:
                # הכנת הנתונים למשלוח (השמות צריכים להתאים לקוד ב-Apps Script)
                payload = {
                    "title": f_title,
                    "author": f_author,
                    "series": f_series,
                    "series_num": f_series_num,
                    "world": f_world,
                    "location": f_location,
                    "publisher": f_publisher,
                    "year": f_year
                }
                
                try:
                    with st.spinner("שומר נתונים..."):
                        res = requests.post(SCRIPT_URL, json=payload)
                        if "Success" in res.text:
                            st.success(f"הספר '{f_title}' נוסף בהצלחה!")
                            st.balloons()
                            st.cache_data.clear() # ניקוי הזיכרון כדי שהספר יופיע בחיפוש
                        else:
                            st.error(f"שגיאה מהשרת: {res.text}")
                except Exception as e:
                    st.error(f"לא הצלחתי לשלוח את הנתונים: {e}")

st.markdown("<br><hr><center><small>ניהול ספריה פרטית v1.5</small></center>", unsafe_allow_html=True)
