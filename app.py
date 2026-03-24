import streamlit as st
import pandas as pd
import os

# הגדרות עמוד
st.set_page_config(page_title="ניהול ספריה", layout="wide")

st.title("📚 בדיקת טעינת ספריה")

# בדיקה אם הקובץ בכלל קיים בשרת
if not os.path.exists('books.csv'):
    st.error("שגיאה: הקובץ 'books.csv' לא נמצא ב-GitHub שלך!")
    st.info("וודא שהעלית את הקובץ וששמו כתוב בדיוק כך (באותיות קטנות).")
else:
    try:
        # ניסיון טעינה עם טיפול בשגיאות
        df = pd.read_csv('books.csv', encoding='utf-8-sig')
        
        # ניקוי נתונים בסיסי
        df = df.dropna(how='all').fillna("")
        df.columns = df.columns.str.strip()
        
        st.success(f"הקובץ נטען בהצלחה! נמצאו {len(df)} ספרים.")
        
        # חיפוש
        search = st.text_input("🔍 חפש ספר או סופר:")
        if search:
            # מחפש את הטקסט בכל העמודות של השורה
            mask = df.apply(lambda row: row.astype(str).str.contains(search, case=False).any(), axis=1)
            results = df[mask]
            
            st.write(f"נמצאו {len(results)} תוצאות:")
            # מציג רק את העמודות החשובות בטבלה
            st.dataframe(results[['שם הספר', 'סופר', 'מיקום_']])
            
    except Exception as e:
        st.error(f"קרתה שגיאה בזמן קריאת הקובץ: {e}")
