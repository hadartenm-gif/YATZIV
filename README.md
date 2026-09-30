# YATZIV Decision — MVP v1

מנוע ניתוח ניהולי וקבלת החלטות לעסקים קטנים.

## הרצה
```bash
pip install -r requirements.txt
streamlit run app.py
```

## מה יש ב-v1
- Business Health: הכנסות, הוצאות, רווחיות ויחסי עלויות.
- Profit Leak: השוואה חודשית של קניות, כוח אדם ורווח.
- Employee Decision: שעתי/חודשי, שעות, שעות יצרניות, עלות מעסיק, Break-even ומרווח ביטחון.
- Pricing Decision: כמה מכירות אפשר לאבד אחרי שינוי מחיר ועדיין לשמור על אותה תרומה.
- What-if: מחזור נדרש ליעד רווח.
- CSV/XLSX upload + demo המבוסס על דוחות החומוסייה שסופקו.

## גבולות מכוונים ב-v1
- אין עדיין OCR/Parser אוטומטי ל-PDF חשבונאי; קודם מייצבים schema ומיפוי.
- אין תזרים אמיתי בלי בנק/מאזן/חייבים/זכאים/מלאי.
- אין קביעה אוטומטית שכל 'קניות' הן COGS.
- חישוב עובד הוא כלי ניהולי, לא תלוש שכר ולא ייעוץ משפטי/חשבונאי.

## Data schema מומלץ
`חודש, הכנסות, הוצאות, קניות, שכר, סוציאליות`

## Next
1. PDF mapper עם אישור משתמש לכל שדה.
2. Balance Sheet + Cash Flow engine.
3. Data confidence per field.
4. Alerts/anomaly detection.
5. Industry benchmark layer only from sourced datasets.
6. AI explanation layer מעל Calculation Engine דטרמיניסטי.
