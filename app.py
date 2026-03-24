import streamlit as st
import pandas as pd
import re

# הגדרות עמוד
st.set_page_config(page_title="הספריה שלי", layout="centered")

# פונקציית עזר להדגשת טקסט
def highlight_search(text, query):
    if not query or not text:
        return text
    # משתמש ב-Regex כדי להחליף את המילה בגרסה מודגשת (לא רגיש לאותיות גדולות/קטנות)
    pattern = re.compile(f"({re.escape(query)})", re.IGNORECASE)
    return pattern.sub(r'<mark style="background-color: yellow;">\1</mark>', str(text))

st.title("📚 חיפוש בספריה")

@st.cache_data
def load_data():
    try:
        # טעינת הקובץ עם קידוד עברי
        df = pd.read_csv('books.csv', encoding='utf-8-sig')
        df = df.dropna(how='all').fillna("")
        df.columns = df.columns.str.strip()
        return df
    except:
        return None

df = load_data()

if df is not None:
    # תיבת החיפוש
    search = st.text_input("🔍 מה לחפש? (ספר, סופר, סדרה או עולם):", placeholder="הקלד כאן...")

    if search:
        # הגדרת העמודות לחיפוש
        search_columns = ['שם הספר', 'סופר', 'שם הסדרה', 'עולם']
        
        # סינון: בודק אם החיפוש קיים באחת מהעמודות
        mask = df[search_columns].apply(lambda row: row.astype(str).str.contains(search, case=False).any(), axis=1)
        results = df[mask]

        if not results.empty:
            st.write(f"נמצאו **{len(results)}** תוצאות:")
            
            for _, row in results.iterrows():
                # הכנת הטקסט להצגה עם הדגשה
                book_name = highlight_search(row['שם הספר'], search)
                author = highlight_search(row['סופר'], search)
                series = highlight_search(row['שם הסדרה'], search)
                world = highlight_search(row['עולם'], search)
                location = row['מיקום_']
                
                # תצוגת כרטיס ספר
                with st.container():
                    st.markdown(f"""
                    <div style="border: 1px solid #ddd; padding: 15px; border-radius: 8px; margin-bottom: 10px; background-color: white;">
                        <div style="font-size: 1.2em; font-weight: bold;">{book_name}</div>
                        <div style="color: #555;">✍️ סופר: {author}</div>
                        <div style="font-size: 0.9em; color: #777;">
                            {f"📖 סדרה: {series}" if row['שם הסדרה'] else ""} 
                            {f" | 🌍 עולם: {world}" if row['עולם'] else ""}
                        </div>
                        <div style="margin-top: 8px; color: #d32f2f; font-weight: bold;">📍 מיקום: {location}</div>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.warning(f"לא נמצאו ספרים עם המילה '{search}'")
    else:
        st.info(f"הספריה טעונה עם {len(df)} ספרים. מחכה לחיפוש שלך...")
else:
    st.error("קובץ ה-CSV לא נמצא או שאינו תקין.")
