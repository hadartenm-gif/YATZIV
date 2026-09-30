import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title='YATZIV Decision', page_icon='📊', layout='wide')

st.markdown('''
<style>
.block-container{padding-top:1.5rem;max-width:1250px}.metric-card{background:#111827;border:1px solid #263247;border-radius:18px;padding:18px}.small{color:#94a3b8;font-size:.85rem}.good{color:#34d399}.warn{color:#fbbf24}.bad{color:#fb7185}
</style>''', unsafe_allow_html=True)

st.title('YATZIV Decision — MVP v1')
st.caption('מנוע ניתוח ניהולי וקבלת החלטות לעסק • הנתונים והחישובים מופרדים מהסבר ה-AI')

DEMO = pd.DataFrame({
    'חודש':['06/2022','07/2022','08/2022','09/2022','10/2022','11/2022','12/2022'],
    'הכנסות':[30242,38210,31143,47881,35432,28890,37069],
    'הוצאות':[56862,32293,56589,61991,37068,31200,50531],
    'קניות':[17551,10581,8693,9904,6229,7150,10735],
    'שכר':[14331,13143,14642,14908,15733,11473,15056],
    'סוציאליות':[3824,467,504,623,5328,982,672],
})
DEMO['רווח_הפסד'] = DEMO['הכנסות']-DEMO['הוצאות']

with st.sidebar:
    st.header('מקור נתונים')
    source = st.radio('בחר', ['דוגמת החומוסייה 2022','העלאת CSV / Excel','הזנה ידנית'])
    st.divider()
    st.caption('גרסת MVP. קריאת PDF חשבונאי אוטומטית תתווסף לאחר שנקבע מיפוי שדות אמין.')

if source == 'דוגמת החומוסייה 2022':
    df = DEMO.copy()
elif source == 'העלאת CSV / Excel':
    f=st.file_uploader('העלה CSV/XLSX', type=['csv','xlsx'])
    if f is None:
        st.info('העלה קובץ כדי להתחיל. עמודות מומלצות: חודש, הכנסות, הוצאות, קניות, שכר, סוציאליות.')
        st.stop()
    try:
        df = pd.read_csv(f) if f.name.lower().endswith('.csv') else pd.read_excel(f)
    except Exception as e:
        st.error(f'לא ניתן לקרוא את הקובץ: {e}'); st.stop()
    required=['חודש','הכנסות','הוצאות']
    missing=[c for c in required if c not in df.columns]
    if missing:
        st.error('חסרות עמודות חובה: '+', '.join(missing)); st.stop()
    for c in ['קניות','שכר','סוציאליות']:
        if c not in df.columns: df[c]=0
    df['רווח_הפסד']=df['הכנסות']-df['הוצאות']
else:
    st.subheader('הזנה ידנית — חודש מייצג')
    c1,c2,c3=st.columns(3)
    rev=c1.number_input('הכנסות חודשיות',0.0,step=1000.0,value=100000.0)
    exp=c2.number_input('סה״כ הוצאות',0.0,step=1000.0,value=85000.0)
    purch=c3.number_input('קניות / עלות ישירה',0.0,step=1000.0,value=30000.0)
    c1,c2=st.columns(2)
    sal=c1.number_input('שכר',0.0,step=1000.0,value=25000.0)
    soc=c2.number_input('סוציאליות/נלוות שכר',0.0,step=500.0,value=4000.0)
    df=pd.DataFrame({'חודש':['נוכחי'],'הכנסות':[rev],'הוצאות':[exp],'קניות':[purch],'שכר':[sal],'סוציאליות':[soc]})
    df['רווח_הפסד']=df['הכנסות']-df['הוצאות']

# normalize numeric
for c in ['הכנסות','הוצאות','קניות','שכר','סוציאליות','רווח_הפסד']:
    df[c]=pd.to_numeric(df[c],errors='coerce').fillna(0)

latest=df.iloc[-1]
total_rev=df['הכנסות'].sum(); total_exp=df['הוצאות'].sum(); total_profit=df['רווח_הפסד'].sum()
active=df[df['הכנסות']>0]
avg_rev=active['הכנסות'].mean() if len(active) else 0
avg_exp=active['הוצאות'].mean() if len(active) else 0
avg_profit=active['רווח_הפסד'].mean() if len(active) else 0

# ratios
purch_pct=(active['קניות'].sum()/total_rev) if total_rev else 0
labor_total=active['שכר'].sum()+active['סוציאליות'].sum()
labor_pct=labor_total/total_rev if total_rev else 0
oper_margin=total_profit/total_rev if total_rev else 0

TABS=st.tabs(['מצב העסק','Profit Leak','עובד חדש','שינוי מחיר','What‑If','נתונים'])

with TABS[0]:
    st.subheader('Business Health')
    a,b,c,d=st.columns(4)
    a.metric('הכנסות בתקופה',f'₪{total_rev:,.0f}')
    b.metric('הוצאות בתקופה',f'₪{total_exp:,.0f}')
    c.metric('רווח / הפסד',f'₪{total_profit:,.0f}',f'{oper_margin:.1%} מהמחזור')
    d.metric('מחזור חודשי ממוצע',f'₪{avg_rev:,.0f}')
    st.markdown('#### תמונת מצב')
    x,y,z=st.columns(3)
    x.metric('קניות / הכנסות',f'{purch_pct:.1%}')
    y.metric('שכר + נלוות / הכנסות',f'{labor_pct:.1%}')
    z.metric('רווח חודשי ממוצע',f'₪{avg_profit:,.0f}')
    if total_profit < 0:
        st.error(f'🔴 בתקופה שנקלטה העסק מציג הפסד מצטבר של ₪{abs(total_profit):,.0f}. יש לפרק את הפער לעלות ישירה, כוח אדם והוצאות קבועות לפני החלטה.')
    elif oper_margin < .05:
        st.warning('🟠 העסק רווחי, אך מרווח הרווח נמוך. שינוי קטן בעלויות או במכירות עלול למחוק את הרווח.')
    else:
        st.success('🟢 העסק רווחי בתקופה שנקלטה. כעת צריך לבדוק איכות רווח, תזרים ורגישות.')
    st.line_chart(df.set_index('חודש')[['הכנסות','הוצאות']])

with TABS[1]:
    st.subheader('Profit Leak Detector')
    tmp=df.copy()
    tmp['קניות %']=np.where(tmp['הכנסות']>0,tmp['קניות']/tmp['הכנסות'],np.nan)
    tmp['כוח אדם %']=np.where(tmp['הכנסות']>0,(tmp['שכר']+tmp['סוציאליות'])/tmp['הכנסות'],np.nan)
    tmp['רווח %']=np.where(tmp['הכנסות']>0,tmp['רווח_הפסד']/tmp['הכנסות'],np.nan)
    st.dataframe(tmp[['חודש','הכנסות','קניות %','כוח אדם %','רווח_הפסד','רווח %']].style.format({'הכנסות':'₪{:,.0f}','קניות %':'{:.1%}','כוח אדם %':'{:.1%}','רווח_הפסד':'₪{:,.0f}','רווח %':'{:.1%}'}),use_container_width=True)
    if len(active)>=2:
        worst=active.loc[active['רווח_הפסד'].idxmin()]
        best=active.loc[active['רווח_הפסד'].idxmax()]
        st.write(f"**החודש החלש ביותר:** {worst['חודש']} — ₪{worst['רווח_הפסד']:,.0f}.  **החזק ביותר:** {best['חודש']} — ₪{best['רווח_הפסד']:,.0f}.")
    st.caption('הערה: בלי מאזן, מלאי, בנק ופירוט ספקים אי אפשר לקבוע שכל קנייה היא Cost of Goods Sold או להסיק תזרים אמיתי.')

with TABS[2]:
    st.subheader('Decision Engine — האם כדאי להעסיק עובד?')
    c1,c2=st.columns(2)
    emp_type=c1.selectbox('סוג העסקה',['שעתי','חודשי'])
    if emp_type=='שעתי':
        hourly=c1.number_input('שכר לשעה ₪',0.0,value=55.0,step=1.0)
        hours=c1.number_input('שעות צפויות בחודש',0.0,value=160.0,step=5.0)
        base=hourly*hours
    else:
        base=c1.number_input('שכר ברוטו חודשי ₪',0.0,value=10000.0,step=500.0)
        hours=c1.number_input('שעות עבודה צפויות בחודש',0.0,value=182.0,step=1.0)
    productive=c2.number_input('שעות יצרניות / Billable צפויות',0.0,value=min(float(hours),120.0),step=5.0)
    extra=c2.number_input('רכב/ציוד/טלפון/הכשרה — חודשי ₪',0.0,value=500.0,step=100.0)
    pension_rate=c2.number_input('הפרשות מעסיק נוספות לחישוב (%)',0.0,50.0,value=12.5,step=.5)/100
    # 2026 NI employer standard resident 18-retirement: 4.51% to 7703, 7.6% above
    ni=min(base,7703)*.0451 + max(0,base-7703)*.076
    loaded=base+ni+base*pension_rate+extra
    cm=st.slider('Contribution Margin של העסק',5,95,int(max(5,min(95,round((1-purch_pct)*100 if total_rev else 50))))) / 100
    expected_rev=st.number_input('כמה הכנסה חודשית נוספת העובד צפוי לייצר? ₪',0.0,value=30000.0,step=1000.0)
    breakeven=loaded/cm if cm else np.inf
    contrib=expected_rev*cm-loaded
    mos=(expected_rev-breakeven)/expected_rev if expected_rev else -1
    a,b,c,d=st.columns(4)
    a.metric('שכר בסיס',f'₪{base:,.0f}')
    b.metric('עלות מעסיק משוערת',f'₪{loaded:,.0f}')
    c.metric('הכנסה לנקודת איזון',f'₪{breakeven:,.0f}')
    d.metric('תרומה חודשית משוערת',f'₪{contrib:,.0f}')
    if contrib<=0: st.error(f'🔴 לפי ההנחות העובד אינו מכסה את עלותו. חסרים כ־₪{max(0,breakeven-expected_rev):,.0f} הכנסה חודשית נוספת כדי להגיע לאיזון.')
    elif mos<.2: st.warning(f'🟠 העובד מכסה את העלות, אבל מרווח הביטחון נמוך ({mos:.0%}). כדאי לבדוק תרחיש שמרני.')
    else: st.success(f'🟢 לפי ההנחות קיים מרווח ביטחון של {mos:.0%} מעל נקודת האיזון.')
    if productive>0:
        st.write(f'עלות כלכלית לשעה יצרנית: **₪{loaded/productive:,.1f}**. נדרשות בערך **{breakeven/max(expected_rev/max(productive,1),1):.0f} שעות** בקצב ההכנסה שהוזן כדי לכסות את העלות.')
    st.caption('עלות המעסיק היא אומדן ניהולי. ביטוח לאומי מחושב כאן לפי מדרגות 2026 לעובד ישראלי רגיל; הפרשות/זכויות נוספות ניתנות לשינוי ולא מחליפות חישוב שכר מקצועי.')

with TABS[3]:
    st.subheader('Decision Engine — שינוי מחיר')
    c1,c2,c3=st.columns(3)
    price=c1.number_input('מחיר נוכחי ליחידה/עסקה',1.0,value=100.0)
    varcost=c2.number_input('עלות משתנה ליחידה/עסקה',0.0,value=40.0)
    qty=c3.number_input('כמות חודשית',1.0,value=1000.0)
    newprice=st.number_input('מחיר חדש',1.0,value=110.0)
    oldcm=(price-varcost)*qty
    newcm_unit=newprice-varcost
    qty_same=oldcm/newcm_unit if newcm_unit>0 else np.inf
    loss_allowed=1-qty_same/qty
    st.metric('ירידה מקסימלית בכמות ועדיין לשמור על אותה תרומה',f'{loss_allowed:.1%}')
    st.write(f'במחיר החדש צריך למכור לפחות **{qty_same:,.0f} יחידות/עסקאות** במקום {qty:,.0f}, בהנחה שהעלות המשתנה ליחידה לא משתנה.')

with TABS[4]:
    st.subheader('What‑If — יעד רווח')
    fixed=st.number_input('הוצאות חודשיות שאינן משתנות ישירות עם המכירות ₪',0.0,value=max(0.0,float(avg_exp-active['קניות'].mean() if len(active) else 50000)),step=1000.0)
    cm2=st.slider('Contribution Margin לתרחיש',5,95,int(cm*100),key='cm2')/100
    target=st.number_input('יעד רווח חודשי ₪',0.0,value=15000.0,step=1000.0)
    need=(fixed+target)/cm2 if cm2 else np.inf
    st.metric('מחזור נדרש',f'₪{need:,.0f}')
    st.write(f'כדי לכסות הוצאות קבועות של ₪{fixed:,.0f} ולהגיע לרווח של ₪{target:,.0f}, נדרש מחזור של כ־**₪{need:,.0f}** בהנחת Contribution Margin של {cm2:.0%}.')

with TABS[5]:
    st.subheader('נתונים שנקלטו')
    st.dataframe(df,use_container_width=True)
    st.download_button('הורד CSV מנורמל',df.to_csv(index=False).encode('utf-8-sig'),'yatziv_normalized.csv','text/csv')
    st.markdown('''**Data Confidence — MVP**\n- Actual: נתון שהגיע מקובץ/דוח\n- User assumption: נתון שהמשתמש הזין לסימולציה\n- System calculation: תוצאה מחושבת\n\nבגרסה הבאה כל שדה יקבל Source + Confidence ולא תוצג מסקנה נחרצת כשהמידע חסר.''')
