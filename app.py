import streamlit as st
import pandas as pd
import re

st.set_page_config(page_title="הספריה שלי", layout="centered")

def highlight_search(text, query):
    if not query or not text: return text
    pattern = re.compile(f"({re.escape(query)})", re.IGNORECASE)
    return pattern.sub(r'<mark style="background-color: yellow; padding: 0 2px;">\1</mark>', str(text))

@st.cache_data(ttl=60) # הורדתי את זמן הזיכרון לדקה אחת בלבד לסנכרון מהיר יותר
def load_live_data():
    sheet_id = "14v7PSy9fKCMVvTvFHdx5ECrwcmrnRok2S5luvfC0O7Q"
    gid = "1314151533"
    csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"
    
    try:
        # טעינה עם הגדרות לטיפול בבעיות פורמט
        df = pd.read_csv(csv_url, on_bad_lines='skip')
        df = df.dropna(how='all').fillna("")
        df.columns = df.columns.str.strip()
        return df
    except Exception as e:
        st.error(f"שגיאה בחיבור לגוגל שיטס: {e}")
        return None

st.title("📚 הספריה שלי")

df = load_live_data()

if df is not None:
    # מציג כמה ספרים נטענו בסך הכל (עוזר לזיהוי חיתוכים)
    st.caption(f"נטענו {len(df)} ספרים מהגוגל שיטס שלך")

    search = st.text_input("🔍 חיפוש:", placeholder="הקלד שם ספר, סופר או סדרה...")

    if search:
        search = search.strip() # ניקוי רווחים מיותרים בחיפוש
        search_columns = ['שם הספר', 'סופר', 'שם הסדרה', 'עולם']
        existing_cols = [col for col in search_columns if col in df.columns]
        
        mask = df[existing_cols].apply(lambda row: row.astype(str).str.contains(search, case=False).any(), axis=1)
        results = df[mask]

        if not results.empty:
            st.write(f"נמצאו **{len(results)}** תוצאות:")
            for _, row in results.iterrows():
                book_name = highlight_search(row.get('שם הספר', ''), search)
                author = highlight_search(row.get('סופר', ''), search)
                series = highlight_search(row.get('שם הסדרה', ''), search)
                world = highlight_search(row.get('עולם', ''), search)
                location = row.get('מיקום_', 'לא צוין')
                
                card_html = (
                    f'<div style="border: 1px solid #ddd; padding: 15px; border-radius: 8px; '
                    f'margin-bottom: 10px; background-color: white; direction: rtl; text-align: right;">'
                    f'<div style="font-size: 1.2em; font-weight: bold; margin-bottom: 5px;">{book_name}</div>'
                    f'<div style="color: #555;">✍️ סופר: {author}</div>'
                    f'<div style="font-size: 0.9em; color: #777; margin-top: 5px;">'
                    f'{"📖 סדרה: " + series if row.get("שם הסדרה") else ""} '
                    f'{" | 🌍 עולם: " + world if row.get("עולם") else ""}</div>'
                    f'<div style="margin-top: 10px; color: #d32f2f; font-weight: bold;">📍 מיקום: {location}</div>'
                    f'</div>'
                )
                st.markdown(card_html, unsafe_allow_html=True)
        else:
            st.warning(f"המילה '{search}' לא נמצאה.")
    
    # הוספת כפתור רענון בולט יותר
    if st.button("🔄 רענן נתונים מהגוגל שיטס"):
        st.cache_data.clear()
        st.rerun()
