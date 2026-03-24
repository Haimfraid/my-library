import streamlit as st
import pandas as pd
import re

# הגדרות עמוד
st.set_page_config(page_title="הספריה שלי", layout="centered")

# פונקציית עזר להדגשת טקסט - משופרת
def highlight_search(text, query):
    if not query or not text:
        return text
    # החלפה בטוחה של המילה בגרסה מודגשת
    pattern = re.compile(f"({re.escape(query)})", re.IGNORECASE)
    return pattern.sub(r'<mark style="background-color: yellow; padding: 0 2px;">\1</mark>', str(text))

st.title("📚 חיפוש בספריה")

@st.cache_data
def load_data():
    try:
        df = pd.read_csv('books.csv', encoding='utf-8-sig')
        df = df.dropna(how='all').fillna("")
        df.columns = df.columns.str.strip()
        return df
    except:
        return None

df = load_data()

if df is not None:
    search = st.text_input("🔍 מה לחפש? (ספר, סופר, סדרה או עולם):", placeholder="הקלד כאן...")

    if search:
        search_columns = ['שם הספר', 'סופר', 'שם הסדרה', 'עולם']
        mask = df[search_columns].apply(lambda row: row.astype(str).str.contains(search, case=False).any(), axis=1)
        results = df[mask]

        if not results.empty:
            st.write(f"נמצאו **{len(results)}** תוצאות:")
            
            for _, row in results.iterrows():
                # הכנת נתונים והדגשה
                book_name = highlight_search(row['שם הספר'], search)
                author = highlight_search(row['סופר'], search)
                series = highlight_search(row['שם הסדרה'], search)
                world = highlight_search(row['עולם'], search)
                location = row['מיקום_']
                
                # בניית חלקי הטקסט בצורה בטוחה
                series_html = f"📖 סדרה: {series}" if row['שם הסדרה'] else ""
                world_html = f" | 🌍 עולם: {world}" if row['עולם'] else ""
                
                # בניית ה-HTML של הכרטיס כמחרוזת אחת ארוכה למניעת בעיות תצוגה
                card_html = (
                    f'<div style="border: 1px solid #ddd; padding: 15px; border-radius: 8px; '
                    f'margin-bottom: 10px; background-color: white; direction: rtl; text-align: right;">'
                    f'<div style="font-size: 1.2em; font-weight: bold; margin-bottom: 5px;">{book_name}</div>'
                    f'<div style="color: #555;">✍️ סופר: {author}</div>'
                    f'<div style="font-size: 0.9em; color: #777; margin-top: 5px;">{series_html}{world_html}</div>'
                    f'<div style="margin-top: 10px; color: #d32f2f; font-weight: bold;">📍 מיקום: {location}</div>'
                    f'</div>'
                )
                
                st.markdown(card_html, unsafe_allow_html=True)
        else:
            st.warning(f"לא נמצאו ספרים עם המילה '{search}'")
    else:
        st.info(f"הספריה טעונה עם {len(df)} ספרים.")
else:
    st.error("לא הצלחתי לטעון את קובץ הנתונים.")
