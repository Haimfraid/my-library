import streamlit as st
import pandas as pd
import re

# הגדרות עמוד - האייקון שיופיע בלשונית בדפדפן
st.set_page_config(page_title="הספריה שלי", page_icon="📚", layout="centered")

# הזרקת קוד שגורם לאנדרואיד/כרום לזהות את האייקון למסך הבית
# השתמשתי בתמונה איכותית של אימוג'י 3 ספרים
icon_url = "https://fonts.gstatic.com/s/e/notoemoji/latest/1f4da/512.png"

st.markdown(f"""
    <head>
        <link rel="apple-touch-icon" href="{icon_url}">
        <link rel="icon" type="image/png" href="{icon_url}">
    </head>
    """, unsafe_allow_html=True)

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
    st.session_state.items_to_show = 20
if 'last_search' not in st.session_state:
    st.session_state.last_search = ""

df = load_live_data()

st.title("📚 הספריה שלי")

if df is not None:
    search = st.text_input("🔍 חפש ספר, סופר או סדרה:", placeholder="הקלד כאן...")

    if search != st.session_state.last_search:
        st.session_state.items_to_show = 20
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
                
                card_html = (
                    f'<div style="border: 1px solid #ddd; padding: 15px; border-radius: 8px; '
                    f'margin-bottom: 10px; background-color: white; direction: rtl; text-align: right;">'
                    f'<div style="font-size: 1.1em; font-weight: bold; margin-bottom: 5px;">{book_name}</div>'
                    f'<div style="color: #555;">✍️ סופר: {author}</div>'
                    f'<div style="font-size: 0.85em; color: #777; margin-top: 5px;">'
                    f'{"📖 סדרה: " + series if row.get("שם הסדרה") else ""} '
                    f'{" | 🌍 עולם: " + world if row.get("עולם") else ""}</div>'
                    f'<div style="margin-top: 10px; color: #d32f2f; font-weight: bold;">📍 מיקום: {row["מיקום_"]}</div>'
                    f'</div>'
                )
                st.markdown(card_html, unsafe_allow_html=True)

            if st.session_state.items_to_show < total_results:
                if st.button(f"הצג עוד תוצאות ({total_results - st.session_state.items_to_show} נותרו)..."):
                    st.session_state.items_to_show += 20
                    st.rerun()
        else:
            st.warning(f"המילה '{search}' לא נמצאה.")
    else:
        st.info(f"בספריה יש {len(df)} ספרים.")
        if st.button("🔄 רענן נתונים"):
            st.cache_data.clear()
            st.rerun()
