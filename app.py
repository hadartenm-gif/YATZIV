import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(page_title='YATZIV Decision', page_icon='Y', layout='wide', initial_sidebar_state='expanded')

# ---------- DESIGN ----------
st.markdown('''
<style>
@import url('https://fonts.googleapis.com/css2?family=Heebo:wght@400;500;600;700;800&display=swap');
html, body, [class*="css"] {font-family:'Heebo',sans-serif; direction:rtl;}
.stApp {background:linear-gradient(135deg,#f7f9ff 0%,#eef4ff 55%,#f8f6ff 100%); color:#17213b;}
.block-container{padding-top:1.1rem;padding-bottom:3rem;max-width:1500px;}
[data-testid="stSidebar"]{background:linear-gradient(180deg,#0b1733 0%,#101d3d 100%);}
[data-testid="stSidebar"] *{color:#eef4ff;}
.hero{background:linear-gradient(120deg,#111f46,#253b82 55%,#6d3df5);padding:24px 28px;border-radius:24px;color:white;box-shadow:0 18px 50px rgba(31,52,115,.18);margin-bottom:16px;}
.hero h1{margin:0;font-size:2.05rem;font-weight:800}.hero p{margin:.35rem 0 0;color:#dbe6ff}
.card{background:rgba(255,255,255,.94);border:1px solid #e4eafd;border-radius:20px;padding:18px 20px;box-shadow:0 8px 26px rgba(42,65,130,.07);height:100%;}
.kpi{background:white;border:1px solid #e6ebfb;border-radius:20px;padding:17px 18px;box-shadow:0 8px 25px rgba(34,55,120,.07);min-height:120px;}
.kpi-label{font-size:.9rem;color:#69738d;font-weight:600}.kpi-value{font-size:1.75rem;font-weight:800;color:#18244a;margin-top:6px}.kpi-sub{font-size:.82rem;color:#8790a8;margin-top:4px}.kpi.bad{background:linear-gradient(135deg,#fff,#fff0f3);border-color:#ffd7df}.kpi.good{background:linear-gradient(135deg,#fff,#ecfff6);border-color:#d2f7e5}.kpi.info{background:linear-gradient(135deg,#fff,#edf4ff);border-color:#dce8ff}
.section-title{font-size:1.25rem;font-weight:800;color:#17244b;margin:.4rem 0 .8rem}.eyebrow{font-size:.78rem;font-weight:700;color:#6d4aff;letter-spacing:.02em}.insight{background:#f6f8ff;border-right:4px solid #6d4aff;border-radius:14px;padding:12px 14px;margin:8px 0}.danger{background:#fff2f4;border-right-color:#f43f5e}.success{background:#edfff6;border-right-color:#10b981}.warning{background:#fff8e8;border-right-color:#f59e0b}
[data-testid="stMetric"]{background:white;border:1px solid #e6ebfb;padding:14px;border-radius:16px;box-shadow:0 5px 18px rgba(34,55,120,.05)}
.stTabs [data-baseweb="tab-list"]{gap:8px;background:white;padding:8px;border-radius:16px;border:1px solid #e7ebf7;}
.stTabs [data-baseweb="tab"]{height:44px;border-radius:11px;padding:0 18px;font-weight:700}.stTabs [aria-selected="true"]{background:#5b3df5;color:white;}
div[data-testid="stDataFrame"]{border:1px solid #e6ebfb;border-radius:16px;overflow:hidden}
.stButton>button,.stDownloadButton>button{border-radius:12px;font-weight:700;min-height:42px}
hr{border-color:#e8ecf7}.muted{color:#7d879f;font-size:.88rem}.pill{display:inline-block;padding:5px 10px;border-radius:999px;background:#eef2ff;color:#4f46e5;font-size:.78rem;font-weight:700;margin-left:5px}
</style>''', unsafe_allow_html=True)

# ---------- HELPERS ----------
def money(x): return f"₪{x:,.0f}"
def pct(x): return f"{x:.1%}"
def safe_div(a,b): return a/b if b else 0

def kpi(label,value,sub='',kind='info'):
    st.markdown(f'<div class="kpi {kind}"><div class="kpi-label">{label}</div><div class="kpi-value">{value}</div><div class="kpi-sub">{sub}</div></div>',unsafe_allow_html=True)

def chart_style(fig, height=330):
    fig.update_layout(height=height,margin=dict(l=15,r=15,t=35,b=15),paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)',font=dict(family='Heebo'),legend=dict(orientation='h',y=1.12,x=.5,xanchor='center'),hovermode='x unified')
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(gridcolor='#edf0f7',zerolinecolor='#dfe5f3')
    return fig

# ---------- REAL CASE STUDY FROM THE PROVIDED 2022 P&L ----------
DEMO = pd.DataFrame({
    'חודש':['05/2022','06/2022','07/2022','08/2022','09/2022','10/2022','11/2022','12/2022'],
    'הכנסות':[0,30242,38210,31143,47881,35432,28890,37069],
    'הוצאות':[2622,56862,32293,56589,61991,37068,31200,50531],
    'קניות':[1597,17551,10581,8693,9904,6229,7150,10735],
    'שכר':[0,14331,13143,14642,14908,15733,11473,15056],
    'סוציאליות':[0,3824,467,504,623,5328,982,672],
})
DEMO['רווח_הפסד']=DEMO['הכנסות']-DEMO['הוצאות']

# ---------- SIDEBAR: FLOW FIRST ----------
with st.sidebar:
    st.markdown('## YATZIV')
    st.caption('Business Decision Engine')
    st.divider()
    st.markdown('### 1 · בחר מקור נתונים')
    source=st.radio('מקור', ['דוגמת החומוסייה 2022','העלאת CSV / Excel','הזנה ידנית'],label_visibility='collapsed')
    st.markdown('### 2 · בדוק את מצב העסק')
    st.caption('התחל ב״תמונת מצב״. אחר כך עבור ל״מה השתנה״ ורק אז לסימולציות.')
    st.markdown('### 3 · קבל החלטה')
    st.caption('עובד חדש · שינוי מחיר · יעד רווח')
    st.divider()
    st.markdown('<span class="pill">Actual</span><span class="pill">Assumption</span><span class="pill">Calculated</span>',unsafe_allow_html=True)
    st.caption('כל מסקנה צריכה להיות מחוברת למקור נתון. אין השלמת מספרים חסרים בניחוש.')

# ---------- DATA INPUT ----------
if source=='דוגמת החומוסייה 2022':
    df=DEMO.copy(); source_label='Case Study · חומוסייה 2022'; confidence='בינונית'
elif source=='העלאת CSV / Excel':
    st.markdown('<div class="hero"><h1>העלאת נתוני העסק</h1><p>העלה קובץ מסודר. קודם נבדוק איכות נתונים, ורק אחר כך נציג מסקנות.</p></div>',unsafe_allow_html=True)
    f=st.file_uploader('CSV / Excel',type=['csv','xlsx'],help='עמודות חובה: חודש, הכנסות, הוצאות. מומלץ גם: קניות, שכר, סוציאליות.')
    if f is None: st.info('העלה קובץ כדי להתחיל.'); st.stop()
    try: df=pd.read_csv(f) if f.name.lower().endswith('.csv') else pd.read_excel(f)
    except Exception as e: st.error(f'לא ניתן לקרוא את הקובץ: {e}'); st.stop()
    missing=[c for c in ['חודש','הכנסות','הוצאות'] if c not in df.columns]
    if missing: st.error('חסרות עמודות חובה: '+', '.join(missing)); st.stop()
    for c in ['קניות','שכר','סוציאליות']:
        if c not in df.columns: df[c]=0
    df['רווח_הפסד']=pd.to_numeric(df['הכנסות'],errors='coerce').fillna(0)-pd.to_numeric(df['הוצאות'],errors='coerce').fillna(0)
    source_label=f'קובץ · {f.name}'; confidence='בינונית'
else:
    st.markdown('<div class="hero"><h1>הזנה ידנית</h1><p>מתאים לבדיקה מהירה של חודש מייצג. לניתוח מגמה עדיף להעלות מספר חודשים.</p></div>',unsafe_allow_html=True)
    a,b,c=st.columns(3)
    rev=a.number_input('הכנסות חודשיות',0.0,value=100000.0,step=1000.0); exp=b.number_input('סה״כ הוצאות',0.0,value=85000.0,step=1000.0); purch=c.number_input('קניות / עלות ישירה',0.0,value=30000.0,step=1000.0)
    a,b=st.columns(2); sal=a.number_input('שכר',0.0,value=25000.0,step=1000.0); soc=b.number_input('סוציאליות / נלוות',0.0,value=4000.0,step=500.0)
    df=pd.DataFrame({'חודש':['נוכחי'],'הכנסות':[rev],'הוצאות':[exp],'קניות':[purch],'שכר':[sal],'סוציאליות':[soc]}); df['רווח_הפסד']=df['הכנסות']-df['הוצאות']
    source_label='הזנה ידנית'; confidence='נמוכה'

for c in ['הכנסות','הוצאות','קניות','שכר','סוציאליות','רווח_הפסד']:
    df[c]=pd.to_numeric(df[c],errors='coerce').fillna(0)

active=df[df['הכנסות']>0].copy()
total_rev=df['הכנסות'].sum(); total_exp=df['הוצאות'].sum(); total_profit=df['רווח_הפסד'].sum(); margin=safe_div(total_profit,total_rev)
avg_rev=active['הכנסות'].mean() if len(active) else 0; avg_profit=active['רווח_הפסד'].mean() if len(active) else 0
purch_total=active['קניות'].sum(); labor_total=(active['שכר']+active['סוציאליות']).sum(); purch_pct=safe_div(purch_total,total_rev); labor_pct=safe_div(labor_total,total_rev)
other=max(0,total_exp-purch_total-labor_total)

# ---------- HEADER ----------
st.markdown(f'''<div class="hero"><div class="eyebrow" style="color:#c9d6ff">YATZIV DECISION</div><h1>העסק שלך, ברור במסך אחד.</h1><p>{source_label} · רמת ביטחון נתונים: {confidence} · קודם מבינים מה קרה, אחר כך מקבלים החלטה.</p></div>''',unsafe_allow_html=True)

# ---------- PRIMARY NAVIGATION ----------
t1,t2,t3,t4,t5=st.tabs(['① תמונת מצב','② מה השתנה?','③ החלטות וסימולציות','④ נתונים ואיכות','⑤ הסבר המודל'])

with t1:
    st.markdown('<div class="section-title">מה קורה בעסק?</div>',unsafe_allow_html=True)
    c1,c2,c3,c4=st.columns(4)
    with c1: kpi('סה״כ הכנסות',money(total_rev),'Actual · בתקופה שנקלטה','good')
    with c2: kpi('סה״כ הוצאות',money(total_exp),'Actual · בתקופה שנקלטה','info')
    with c3: kpi('רווח / הפסד',money(total_profit),f'{pct(margin)} מהמחזור','bad' if total_profit<0 else 'good')
    with c4: kpi('מחזור חודשי ממוצע',money(avg_rev),f'{len(active)} חודשים עם הכנסות','info')

    st.markdown('<div class="section-title">הסיפור במספרים</div>',unsafe_allow_html=True)
    left,right=st.columns([1.7,1])
    with left:
        fig=go.Figure()
        fig.add_bar(x=df['חודש'],y=df['הכנסות'],name='הכנסות',marker_color='#2f80ed')
        fig.add_bar(x=df['חודש'],y=df['הוצאות'],name='הוצאות',marker_color='#ff5b6e')
        fig.add_scatter(x=df['חודש'],y=df['רווח_הפסד'],name='רווח / הפסד',mode='lines+markers',line=dict(color='#6c4cf5',width=3))
        st.plotly_chart(chart_style(fig,360),use_container_width=True,config={'displayModeBar':False})
    with right:
        labels=['קניות','שכר + סוציאליות','יתר הוצאות']; vals=[purch_total,labor_total,other]
        fig2=go.Figure(go.Pie(labels=labels,values=vals,hole=.62,marker=dict(colors=['#ff9f43','#4f7cff','#9b5de5'])))
        fig2.update_layout(height=360,margin=dict(l=5,r=5,t=20,b=5),paper_bgcolor='rgba(0,0,0,0)',font=dict(family='Heebo'),showlegend=True,legend=dict(orientation='h',y=-.05))
        st.plotly_chart(fig2,use_container_width=True,config={'displayModeBar':False})

    st.markdown('<div class="section-title">מה דורש תשומת לב עכשיו?</div>',unsafe_allow_html=True)
    if total_profit<0:
        st.markdown(f'<div class="insight danger"><b>העסק הפסיד {money(abs(total_profit))} בתקופה.</b><br>לפני כל הרחבה או גיוס, צריך להבין אילו עלויות הן שוטפות ואילו היו חד־פעמיות/הקמה.</div>',unsafe_allow_html=True)
    st.markdown(f'<div class="insight"><b>כוח אדם:</b> {pct(labor_pct)} מההכנסות שנקלטו. זה יחס ניהולי בלבד — בלי שעות עבודה ותפקידים עדיין אי אפשר לקבוע אם הוא גבוה או נמוך.</div>',unsafe_allow_html=True)
    st.markdown(f'<div class="insight warning"><b>קניות:</b> {pct(purch_pct)} מהמחזור. בדוח רווח והפסד קניות אינן בהכרח זהות לעלות מזון שנצרך; בלי מלאי פתיחה/סגירה לא נסמן זאת כ־Food Cost סופי.</div>',unsafe_allow_html=True)

with t2:
    st.markdown('<div class="section-title">Profit Leak · איפה התוצאה השתנתה?</div>',unsafe_allow_html=True)
    tmp=df.copy(); tmp['קניות %']=np.where(tmp['הכנסות']>0,tmp['קניות']/tmp['הכנסות'],np.nan); tmp['כוח אדם %']=np.where(tmp['הכנסות']>0,(tmp['שכר']+tmp['סוציאליות'])/tmp['הכנסות'],np.nan); tmp['רווח %']=np.where(tmp['הכנסות']>0,tmp['רווח_הפסד']/tmp['הכנסות'],np.nan)
    if len(active)>=2:
        best=active.loc[active['רווח_הפסד'].idxmax()]; worst=active.loc[active['רווח_הפסד'].idxmin()]
        a,b,c=st.columns(3)
        with a: kpi('החודש החזק',str(best['חודש']),money(best['רווח_הפסד']),'good')
        with b: kpi('החודש החלש',str(worst['חודש']),money(worst['רווח_הפסד']),'bad')
        with c: kpi('פער בין החזק לחלש',money(best['רווח_הפסד']-worst['רווח_הפסד']),'דורש פירוק לגורמים','info')
    st.dataframe(tmp[['חודש','הכנסות','הוצאות','קניות %','כוח אדם %','רווח_הפסד','רווח %']].style.format({'הכנסות':'₪{:,.0f}','הוצאות':'₪{:,.0f}','קניות %':'{:.1%}','כוח אדם %':'{:.1%}','רווח_הפסד':'₪{:,.0f}','רווח %':'{:.1%}'}),use_container_width=True,hide_index=True)
    st.markdown('<div class="insight"><b>השלב הבא במנוע:</b> כאשר יהיו לנו ספקים, מלאי, שעות עובדים ובנק — המערכת תוכל לעבור מ״מה השתנה״ ל״למה זה השתנה״ ברמת גורם.</div>',unsafe_allow_html=True)

with t3:
    st.markdown('<div class="section-title">קודם בוחרים החלטה — ורק אז רואים את המספרים הרלוונטיים</div>',unsafe_allow_html=True)
    decision=st.segmented_control('מה אתה רוצה לבדוק?',['עובד חדש','שינוי מחיר','יעד רווח'],default='עובד חדש')
    if decision=='עובד חדש':
        st.markdown('#### האם עובד חדש מכסה את עצמו?')
        a,b=st.columns([1,1])
        with a:
            emp_type=st.selectbox('סוג העסקה',['שעתי','חודשי'])
            if emp_type=='שעתי':
                hourly=st.number_input('שכר לשעה ₪',0.0,value=55.0,step=1.0); hours=st.number_input('שעות בחודש',0.0,value=160.0,step=5.0); base=hourly*hours
            else:
                base=st.number_input('שכר ברוטו חודשי ₪',0.0,value=10000.0,step=500.0); hours=st.number_input('שעות בחודש',0.0,value=182.0,step=1.0)
            productive=st.number_input('שעות יצרניות / מחויבות ללקוח',0.0,value=min(float(hours),120.0),step=5.0)
            extra=st.number_input('ציוד / רכב / טלפון / הכשרה — חודשי ₪',0.0,value=500.0,step=100.0)
            pension_rate=st.number_input('הפרשות מעסיק נוספות לאומדן (%)',0.0,50.0,value=12.5,step=.5)/100
        with b:
            default_cm=int(max(5,min(95,round((1-purch_pct)*100 if total_rev else 50))))
            cm=st.slider('Contribution Margin',5,95,default_cm)/100
            expected_rev=st.number_input('הכנסה חודשית נוספת שהעובד צפוי לייצר ₪',0.0,value=30000.0,step=1000.0)
            ni=min(base,7703)*.0451+max(0,base-7703)*.076
            loaded=base+ni+base*pension_rate+extra; breakeven=loaded/cm if cm else np.inf; contrib=expected_rev*cm-loaded; mos=safe_div(expected_rev-breakeven,expected_rev) if expected_rev else -1
            x,y=st.columns(2); x.metric('עלות מעסיק משוערת',money(loaded)); y.metric('הכנסה לנקודת איזון',money(breakeven))
            x,y=st.columns(2); x.metric('תרומה חודשית',money(contrib)); y.metric('עלות לשעה יצרנית',money(loaded/productive) if productive else '—')
            if contrib<=0: st.error(f'לפי ההנחות חסרות כ־{money(max(0,breakeven-expected_rev))} הכנסות בחודש כדי להגיע לאיזון.')
            elif mos<.2: st.warning(f'מכסה עלות, אבל מרווח הביטחון רק {mos:.0%}.')
            else: st.success(f'לפי ההנחות מרווח הביטחון הוא {mos:.0%}.')
        st.caption('החישוב הוא סימולציה ניהולית. שיעורי עלות מעסיק/זכויות דורשים אימות לפי סוג העובד והתקופה.')
    elif decision=='שינוי מחיר':
        a,b,c=st.columns(3); price=a.number_input('מחיר נוכחי',1.0,value=100.0); varcost=b.number_input('עלות משתנה ליחידה',0.0,value=40.0); qty=c.number_input('כמות חודשית',1.0,value=1000.0)
        newprice=st.number_input('מחיר חדש',1.0,value=110.0); oldcm=(price-varcost)*qty; newcmu=newprice-varcost; qty_same=oldcm/newcmu if newcmu>0 else np.inf; loss_allowed=1-qty_same/qty
        a,b=st.columns(2); a.metric('ירידה מקסימלית בכמות',pct(loss_allowed)); b.metric('כמות מינימום לשמירת אותה תרומה',f'{qty_same:,.0f}')
        st.info('זהו חישוב Contribution בלבד. הוא לא מניח מה תהיה תגובת הלקוחות למחיר החדש.')
    else:
        default_fixed=max(0.0,float((active['הוצאות']-active['קניות']).mean() if len(active) else 50000))
        fixed=st.number_input('הוצאות חודשיות שאינן משתנות ישירות עם המכירות ₪',0.0,value=default_fixed,step=1000.0)
        cm2=st.slider('Contribution Margin לתרחיש',5,95,int(max(5,min(95,round((1-purch_pct)*100 if total_rev else 50)))))/100
        target=st.number_input('יעד רווח חודשי ₪',0.0,value=15000.0,step=1000.0); need=(fixed+target)/cm2 if cm2 else np.inf
        a,b,c=st.columns(3); a.metric('מחזור נדרש',money(need)); b.metric('מחזור ממוצע כיום',money(avg_rev)); c.metric('פער למחזור הנדרש',money(need-avg_rev))

with t4:
    st.markdown('<div class="section-title">הנתונים שעליהם המסקנות מבוססות</div>',unsafe_allow_html=True)
    a,b,c=st.columns(3); a.metric('שורות נתונים',len(df)); b.metric('חודשים עם הכנסה',len(active)); c.metric('רמת ביטחון',confidence)
    st.dataframe(df,use_container_width=True,hide_index=True)
    st.download_button('הורד נתונים מנורמלים CSV',df.to_csv(index=False).encode('utf-8-sig'),'yatziv_normalized.csv','text/csv',use_container_width=True)
    st.markdown('''<div class="insight warning"><b>מה עדיין חסר לניתוח מלא:</b> מאזן, בנק, מלאי, גיול לקוחות/ספקים, הלוואות ושעות עובדים. לכן V2 לא מציג תזרים, DSCR או Food Cost כאילו הם ידועים.</div>''',unsafe_allow_html=True)

with t5:
    st.markdown('<div class="section-title">איך YATZIV חושב?</div>',unsafe_allow_html=True)
    st.markdown('''
    **1. Actual** — נתון שהגיע מדוח/קובץ.  
    **2. Assumption** — הנחה שהמשתמש מזין לסימולציה.  
    **3. Calculated** — תוצאה של נוסחה דטרמיניסטית.  
    **4. Insight** — הסבר עסקי שמבוסס רק על מה שהנתונים מאפשרים להסיק.

    הסדר מכוון: **מצב העסק → שינוי/חריגה → החלטה → בדיקת מקור הנתונים**. כך המשתמש לא קופץ ישר לסימולציה לפני שהבין את העסק.
    ''')
    st.info('בשלב הבא: Parser לדוחות + מיפוי חשבונות + Confidence לכל שדה + Root Cause אוטומטי + תרחיש שמרני/בסיס/חזק.')
