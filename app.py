import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="YATZIV Decision", page_icon="◈", layout="wide", initial_sidebar_state="expanded")

# -------------------- THEME --------------------
st.markdown(r'''
<style>
@import url('https://fonts.googleapis.com/css2?family=Heebo:wght@400;500;600;700;800;900&display=swap');
:root{--ink:#0d1633;--muted:#6d7893;--line:#e7ebf5;--blue:#3974ff;--violet:#7454ff;--green:#17b77e;--red:#f14f6a;--amber:#f2a33a;}
html,body,[class*="css"]{font-family:'Heebo',sans-serif;direction:rtl}.stApp{background:#f5f7fc;color:var(--ink)}
.block-container{max-width:1480px;padding-top:1.1rem;padding-bottom:4rem}
[data-testid="stSidebar"]{background:linear-gradient(180deg,#091229,#0c1734 65%,#101a3a);border-left:1px solid #1d2a4d}
[data-testid="stSidebar"] *{color:#eef3ff}.stRadio>div{gap:.3rem}
[data-testid="stSidebar"] [role="radiogroup"] label{padding:.65rem .75rem;border-radius:12px}
[data-testid="stSidebar"] [role="radiogroup"] label:hover{background:#162650}
.brand{font-size:1.55rem;font-weight:900;letter-spacing:.08em}.brand-sub{font-size:.78rem;color:#9fb0d8;margin-top:-5px}
.topbar{display:flex;justify-content:space-between;align-items:center;background:#fff;border:1px solid var(--line);border-radius:18px;padding:14px 18px;margin-bottom:14px;box-shadow:0 6px 22px rgba(25,44,91,.05)}
.hero{position:relative;overflow:hidden;background:linear-gradient(125deg,#0d1c45 0%,#183777 55%,#6d4bf5 100%);border-radius:24px;padding:25px 28px;color:#fff;box-shadow:0 18px 45px rgba(30,48,110,.18);margin-bottom:15px}
.hero:after{content:'';position:absolute;width:300px;height:300px;border-radius:50%;background:rgba(255,255,255,.08);left:-70px;top:-150px}.hero h1{font-size:2rem;margin:3px 0;font-weight:900}.hero p{color:#dbe5ff;margin:0}
.level{display:inline-flex;gap:8px;align-items:center;background:rgba(255,255,255,.12);padding:7px 11px;border-radius:999px;font-size:.8rem;font-weight:700}
.grid-card{background:#fff;border:1px solid var(--line);border-radius:20px;padding:18px;box-shadow:0 8px 28px rgba(25,44,91,.055);height:100%}
.kpi{background:#fff;border:1px solid var(--line);border-radius:18px;padding:16px 17px;min-height:118px;box-shadow:0 7px 24px rgba(25,44,91,.05);position:relative;overflow:hidden}.kpi:before{content:'';position:absolute;right:0;top:0;width:5px;height:100%;background:#3974ff}.kpi.good:before{background:var(--green)}.kpi.bad:before{background:var(--red)}.kpi.warn:before{background:var(--amber)}
.kpi-label{font-size:.84rem;color:var(--muted);font-weight:700}.kpi-value{font-size:1.7rem;font-weight:900;margin:.25rem 0;color:var(--ink)}.kpi-sub{font-size:.78rem;color:#8b94a9}
.section{font-size:1.25rem;font-weight:900;margin:.65rem 0 .75rem}.section small{font-size:.8rem;font-weight:500;color:var(--muted);margin-right:8px}
.quest{background:#fff;border:1px solid var(--line);border-radius:17px;padding:14px 16px;margin-bottom:9px}.quest-head{display:flex;justify-content:space-between;gap:12px;align-items:center}.quest-title{font-weight:800}.quest-text{font-size:.87rem;color:var(--muted);margin-top:3px}.badge{display:inline-block;padding:5px 9px;border-radius:999px;font-size:.74rem;font-weight:800}.badge.red{background:#fff0f3;color:#d62e50}.badge.green{background:#eafbf4;color:#07875b}.badge.amber{background:#fff6e7;color:#b86c00}.badge.blue{background:#edf3ff;color:#2459c9}
.callout{border-radius:16px;padding:14px 16px;margin:9px 0;border:1px solid #e5e9f5;background:#fff}.callout.red{background:#fff5f6;border-color:#ffdce3}.callout.green{background:#f0fcf7;border-color:#d6f5e7}.callout.amber{background:#fff9ef;border-color:#ffe8c1}.callout.blue{background:#f2f6ff;border-color:#dce7ff}
.progress-wrap{background:#e9edf6;border-radius:999px;height:9px;overflow:hidden}.progress-fill{height:100%;border-radius:999px;background:linear-gradient(90deg,#3974ff,#7655ff)}
.stButton>button,.stDownloadButton>button{border-radius:13px;min-height:44px;font-weight:800;border:1px solid #dfe5f2}.stButton>button[kind="primary"]{background:linear-gradient(90deg,#3974ff,#7655ff);border:0}
[data-testid="stMetric"]{background:#fff;border:1px solid var(--line);border-radius:16px;padding:12px 14px;box-shadow:0 5px 18px rgba(25,44,91,.04)}
div[data-testid="stDataFrame"]{border:1px solid var(--line);border-radius:15px;overflow:hidden}
[data-baseweb="select"]>div,[data-baseweb="input"]>div{border-radius:12px!important}.muted{color:var(--muted);font-size:.84rem}.tiny{font-size:.75rem;color:#8c96ad}
hr{border-color:#e7ebf5}
</style>
''', unsafe_allow_html=True)

# -------------------- HELPERS --------------------
def money(x): return f"₪{x:,.0f}"
def pct(x): return f"{x:.1%}"
def safe_div(a,b): return a/b if b else 0

def kpi(label,value,sub="",kind=""):
    st.markdown(f'<div class="kpi {kind}"><div class="kpi-label">{label}</div><div class="kpi-value">{value}</div><div class="kpi-sub">{sub}</div></div>',unsafe_allow_html=True)

def plot_layout(fig,height=330):
    fig.update_layout(height=height,margin=dict(l=10,r=10,t=25,b=10),paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)',font=dict(family='Heebo',color='#53607b'),legend=dict(orientation='h',y=1.12,x=.5,xanchor='center'),hovermode='x unified')
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(gridcolor='#edf0f6',zerolinecolor='#dce2ef')
    return fig

def callout(title,text,kind='blue'):
    st.markdown(f'<div class="callout {kind}"><b>{title}</b><br><span class="muted">{text}</span></div>',unsafe_allow_html=True)

# -------------------- DEMO: PROVIDED 2022 P&L --------------------
DEMO=pd.DataFrame({
    'חודש':['05/2022','06/2022','07/2022','08/2022','09/2022','10/2022','11/2022','12/2022'],
    'הכנסות':[0,30242,38210,31143,47881,35432,28890,37069],
    'הוצאות':[2622,56862,32293,56589,61991,37068,31200,50531],
    'קניות':[1597,17551,10581,8693,9904,6229,7150,10735],
    'שכר':[0,14331,13143,14642,14908,15733,11473,15056],
    'סוציאליות':[0,3824,467,504,623,5328,982,672],
})
DEMO['רווח_הפסד']=DEMO['הכנסות']-DEMO['הוצאות']

# -------------------- SIDEBAR / SOURCE --------------------
with st.sidebar:
    st.markdown('<div class="brand">◈ YATZIV</div><div class="brand-sub">BUSINESS DECISION ENGINE</div>',unsafe_allow_html=True)
    st.divider()
    page=st.radio('ניווט',['🏠  מרכז שליטה','🔎  איפה הכסף?','🎯  מעבדת החלטות','📁  נתונים','🧠  איך זה עובד'],label_visibility='collapsed')
    st.divider()
    st.markdown('##### מקור נתונים')
    source=st.selectbox('מקור',['דוגמת החומוסייה 2022','העלאת CSV / Excel','הזנה ידנית'],label_visibility='collapsed')
    st.caption('המערכת מפרידה בין נתון אמיתי, הנחת משתמש וחישוב.')

# -------------------- DATA --------------------
if source=='דוגמת החומוסייה 2022':
    df=DEMO.copy(); source_label='חומוסייה · 2022'; confidence='בינונית'; conf_score=62
elif source=='העלאת CSV / Excel':
    f=st.file_uploader('העלה CSV / Excel',type=['csv','xlsx'])
    if f is None:
        st.info('העלה קובץ. עמודות חובה: חודש, הכנסות, הוצאות.'); st.stop()
    try: df=pd.read_csv(f) if f.name.lower().endswith('.csv') else pd.read_excel(f)
    except Exception as e: st.error(f'לא ניתן לקרוא את הקובץ: {e}'); st.stop()
    missing=[c for c in ['חודש','הכנסות','הוצאות'] if c not in df.columns]
    if missing: st.error('חסרות עמודות חובה: '+', '.join(missing)); st.stop()
    for c in ['קניות','שכר','סוציאליות']:
        if c not in df.columns: df[c]=0
    df['רווח_הפסד']=pd.to_numeric(df['הכנסות'],errors='coerce').fillna(0)-pd.to_numeric(df['הוצאות'],errors='coerce').fillna(0)
    source_label=f.name; confidence='בינונית'; conf_score=60
else:
    st.markdown('### הזנה ידנית')
    a,b,c=st.columns(3)
    rev=a.number_input('הכנסות',0.0,value=100000.0,step=1000.0); exp=b.number_input('הוצאות',0.0,value=85000.0,step=1000.0); purch=c.number_input('קניות / עלות ישירה',0.0,value=30000.0,step=1000.0)
    a,b=st.columns(2); sal=a.number_input('שכר',0.0,value=25000.0,step=1000.0); soc=b.number_input('סוציאליות',0.0,value=4000.0,step=500.0)
    df=pd.DataFrame({'חודש':['נוכחי'],'הכנסות':[rev],'הוצאות':[exp],'קניות':[purch],'שכר':[sal],'סוציאליות':[soc]}); df['רווח_הפסד']=df['הכנסות']-df['הוצאות']
    source_label='הזנה ידנית'; confidence='נמוכה'; conf_score=35

for c in ['הכנסות','הוצאות','קניות','שכר','סוציאליות','רווח_הפסד']:
    df[c]=pd.to_numeric(df[c],errors='coerce').fillna(0)
active=df[df['הכנסות']>0].copy()
total_rev=float(df['הכנסות'].sum()); total_exp=float(df['הוצאות'].sum()); total_profit=float(df['רווח_הפסד'].sum()); margin=safe_div(total_profit,total_rev)
avg_rev=float(active['הכנסות'].mean()) if len(active) else 0
purch_total=float(active['קניות'].sum()); labor_total=float((active['שכר']+active['סוציאליות']).sum()); other=max(0,total_exp-purch_total-labor_total)
purch_pct=safe_div(purch_total,total_rev); labor_pct=safe_div(labor_total,total_rev)

# -------------------- TOP --------------------
st.markdown(f'<div class="topbar"><div><b>{source_label}</b><div class="tiny">מקור פעיל לניתוח</div></div><div><span class="badge blue">Data confidence · {conf_score}%</span></div></div>',unsafe_allow_html=True)

# -------------------- CONTROL CENTER --------------------
if page.startswith('🏠'):
    status='דורש טיפול' if total_profit<0 else 'יציב'
    st.markdown(f'''<div class="hero"><div class="level">LEVEL 01 · BUSINESS CONTROL</div><h1>מרכז השליטה של העסק</h1><p>לא דוח חשבונאי. קודם רואים מה חשוב, אחר כך נכנסים לעומק ומקבלים החלטה.</p></div>''',unsafe_allow_html=True)
    a,b,c,d=st.columns(4)
    with a:kpi('מחזור',money(total_rev),'Actual · התקופה שנקלטה','good')
    with b:kpi('הוצאות',money(total_exp),'Actual · התקופה שנקלטה','warn')
    with c:kpi('רווח / הפסד',money(total_profit),pct(margin)+' מהמחזור','bad' if total_profit<0 else 'good')
    with d:kpi('מצב',status,f'{len(active)} חודשים עם פעילות','bad' if total_profit<0 else 'good')

    st.markdown('<div class="section">3 משימות עכשיו <small>לפי סדר עדיפות</small></div>',unsafe_allow_html=True)
    q1,q2,q3=st.columns(3)
    with q1:
        st.markdown(f'<div class="quest"><div class="quest-head"><div class="quest-title">1 · עצור את ההפסד</div><span class="badge red">קריטי</span></div><div class="quest-text">התקופה מסתיימת ב־{money(total_profit)}. לפני צמיחה צריך להבין מה קבוע, מה משתנה ומה חד־פעמי.</div></div>',unsafe_allow_html=True)
    with q2:
        st.markdown(f'<div class="quest"><div class="quest-head"><div class="quest-title">2 · פרק כוח אדם</div><span class="badge amber">בדיקה</span></div><div class="quest-text">שכר + סוציאליות הם {pct(labor_pct)} מהמחזור שנקלט. חסרות שעות ותפקידים כדי לקבוע יעילות.</div></div>',unsafe_allow_html=True)
    with q3:
        st.markdown(f'<div class="quest"><div class="quest-head"><div class="quest-title">3 · בדוק קניות</div><span class="badge blue">ניתוח</span></div><div class="quest-text">קניות הן {pct(purch_pct)} מהמחזור. בלי מלאי פתיחה/סגירה זה עדיין לא Food Cost סופי.</div></div>',unsafe_allow_html=True)

    left,right=st.columns([1.7,1])
    with left:
        st.markdown('<div class="section">מסלול העסק <small>הכנסות · הוצאות · תוצאה</small></div>',unsafe_allow_html=True)
        fig=go.Figure()
        fig.add_bar(x=df['חודש'],y=df['הכנסות'],name='הכנסות',marker_color='#3974ff',marker_line_width=0)
        fig.add_bar(x=df['חודש'],y=df['הוצאות'],name='הוצאות',marker_color='#f14f6a',marker_line_width=0)
        fig.add_scatter(x=df['חודש'],y=df['רווח_הפסד'],name='רווח/הפסד',mode='lines+markers',line=dict(color='#7454ff',width=3),marker=dict(size=7))
        st.plotly_chart(plot_layout(fig,350),use_container_width=True,config={'displayModeBar':False})
    with right:
        st.markdown('<div class="section">לאן הכסף הולך?</div>',unsafe_allow_html=True)
        fig=go.Figure(go.Pie(labels=['קניות','שכר + סוציאליות','יתר הוצאות'],values=[purch_total,labor_total,other],hole=.68,marker=dict(colors=['#f2a33a','#3974ff','#7454ff']),textinfo='percent'))
        fig.update_layout(height=350,margin=dict(l=5,r=5,t=20,b=5),paper_bgcolor='rgba(0,0,0,0)',font=dict(family='Heebo'),legend=dict(orientation='h',y=-.08))
        st.plotly_chart(fig,use_container_width=True,config={'displayModeBar':False})

    st.markdown('<div class="section">התקדמות להבנת העסק</div>',unsafe_allow_html=True)
    st.markdown(f'<div class="progress-wrap"><div class="progress-fill" style="width:{conf_score}%"></div></div><div class="tiny" style="margin-top:6px">{conf_score}% · יש רווח והפסד חודשי. חסרים בנק, מלאי, לקוחות/ספקים, הלוואות ושעות עובדים.</div>',unsafe_allow_html=True)

# -------------------- MONEY MAP --------------------
elif page.startswith('🔎'):
    st.markdown('<div class="hero"><div class="level">LEVEL 02 · PROFIT LEAK</div><h1>איפה הכסף?</h1><p>מסך אחד שמתחיל מהחודש החריג ורק אחר כך יורד לסעיפי העלות.</p></div>',unsafe_allow_html=True)
    if len(active):
        best=active.loc[active['רווח_הפסד'].idxmax()]; worst=active.loc[active['רווח_הפסד'].idxmin()]
        a,b,c=st.columns(3)
        with a:kpi('החודש החזק',str(best['חודש']),money(best['רווח_הפסד']),'good')
        with b:kpi('החודש החלש',str(worst['חודש']),money(worst['רווח_הפסד']),'bad')
        with c:kpi('פער ביצועים',money(best['רווח_הפסד']-worst['רווח_הפסד']),'בין החודש החזק לחלש','warn')
    tmp=df.copy(); tmp['קניות %']=np.where(tmp['הכנסות']>0,tmp['קניות']/tmp['הכנסות'],np.nan); tmp['כוח אדם %']=np.where(tmp['הכנסות']>0,(tmp['שכר']+tmp['סוציאליות'])/tmp['הכנסות'],np.nan); tmp['רווח %']=np.where(tmp['הכנסות']>0,tmp['רווח_הפסד']/tmp['הכנסות'],np.nan)
    st.markdown('<div class="section">לוח חודשי</div>',unsafe_allow_html=True)
    st.dataframe(tmp[['חודש','הכנסות','הוצאות','קניות %','כוח אדם %','רווח_הפסד','רווח %']].style.format({'הכנסות':'₪{:,.0f}','הוצאות':'₪{:,.0f}','קניות %':'{:.1%}','כוח אדם %':'{:.1%}','רווח_הפסד':'₪{:,.0f}','רווח %':'{:.1%}'}),use_container_width=True,hide_index=True)
    callout('מה המנוע יודע כרגע','הוא יודע לזהות באיזה חודש התוצאה הידרדרה ואילו קבוצות עלות השתנו. הוא עדיין לא יכול לייחס את הסיבה לספק/עובד/מוצר בלי פירוט נוסף.','blue')
    callout('כלל בטיחות','לא נסמן קניות כעלות מזון סופית בלי תנועות מלאי, ולא נסיק ששכר גבוה/נמוך בלי שעות ותפוקה.','amber')

# -------------------- DECISION LAB --------------------
elif page.startswith('🎯'):
    st.markdown('<div class="hero"><div class="level">LEVEL 03 · DECISION LAB</div><h1>מעבדת החלטות</h1><p>בחר החלטה אחת. המסך מציג רק את הנתונים שצריך עבורה — בלי עומס.</p></div>',unsafe_allow_html=True)
    decision=st.radio('בחר משימה',['👤 עובד חדש','🏷️ שינוי מחיר','🏁 יעד רווח'],horizontal=True,label_visibility='collapsed')
    st.divider()
    if 'עובד' in decision:
        st.markdown('<div class="section">האם העובד מכסה את עצמו?</div>',unsafe_allow_html=True)
        a,b=st.columns([1,1])
        with a:
            emp_type=st.selectbox('סוג העסקה',['שעתי','חודשי'])
            if emp_type=='שעתי':
                hourly=st.number_input('שכר לשעה ₪',0.0,value=55.0,step=1.0); hours=st.number_input('שעות בחודש',0.0,value=160.0,step=5.0); base=hourly*hours
            else:
                base=st.number_input('ברוטו חודשי ₪',0.0,value=10000.0,step=500.0); hours=st.number_input('שעות בחודש',0.0,value=182.0,step=1.0)
            productive=st.number_input('שעות יצרניות',0.0,value=min(float(hours),120.0),step=5.0)
            extra=st.number_input('עלות חודשית נוספת ₪',0.0,value=500.0,step=100.0)
            employer_extra=st.number_input('הפרשות/עלויות מעסיק נוספות לאומדן (%)',0.0,50.0,value=12.5,step=.5)/100
        with b:
            default_cm=int(max(5,min(95,round((1-purch_pct)*100 if total_rev else 50))))
            cm=st.slider('Contribution Margin',5,95,default_cm)/100
            expected_rev=st.number_input('הכנסה חודשית נוספת צפויה ₪',0.0,value=30000.0,step=1000.0)
            # NI here is a user-facing estimate for scenario testing, not a legal payroll calculator.
            ni=min(base,7703)*.0451+max(0,base-7703)*.076
            loaded=base+ni+base*employer_extra+extra; breakeven=loaded/cm if cm else np.inf; contribution=expected_rev*cm-loaded; mos=safe_div(expected_rev-breakeven,expected_rev) if expected_rev else -1
            x,y=st.columns(2); x.metric('עלות משוערת',money(loaded)); y.metric('מחזור לאיזון',money(breakeven))
            x,y=st.columns(2); x.metric('תרומה אחרי העובד',money(contribution)); y.metric('עלות לשעה יצרנית',money(loaded/productive) if productive else '—')
            if contribution<=0: callout('לא מגיע לאיזון',f'חסרות בערך {money(max(0,breakeven-expected_rev))} הכנסות חודשיות לפי ההנחות.','red')
            elif mos<.2: callout('עובר — אבל צפוף',f'מרווח הביטחון הוא {mos:.0%}. שינוי קטן במכירות יכול למחוק את הכדאיות.','amber')
            else: callout('עובר את הסימולציה',f'מרווח הביטחון לפי ההנחות הוא {mos:.0%}.','green')
        st.caption('הסימולציה אינה מחשבון שכר משפטי. יש לאמת עלויות מעסיק לפי העובד, התקופה וההסכם.')
    elif 'מחיר' in decision:
        a,b,c=st.columns(3); price=a.number_input('מחיר נוכחי',1.0,value=100.0); varcost=b.number_input('עלות משתנה ליחידה',0.0,value=40.0); qty=c.number_input('כמות חודשית',1.0,value=1000.0)
        newprice=st.number_input('מחיר חדש',1.0,value=110.0); old_contribution=(price-varcost)*qty; new_cmu=newprice-varcost; qty_same=old_contribution/new_cmu if new_cmu>0 else np.inf; loss_allowed=1-qty_same/qty
        a,b=st.columns(2); a.metric('מקסימום ירידה בכמות',pct(loss_allowed)); b.metric('כמות מינימום',f'{qty_same:,.0f}')
        callout('איך לקרוא את זה','זו נקודת איזון של תרומה בלבד. המערכת לא מניחה שהלקוחות אכן יקנו באותה כמות אחרי שינוי המחיר.','blue')
    else:
        default_fixed=max(0.0,float((active['הוצאות']-active['קניות']).mean() if len(active) else 50000))
        fixed=st.number_input('הוצאות חודשיות שאינן משתנות ישירות עם המכירות ₪',0.0,value=default_fixed,step=1000.0)
        cm2=st.slider('Contribution Margin לתרחיש',5,95,int(max(5,min(95,round((1-purch_pct)*100 if total_rev else 50)))))/100
        target=st.number_input('יעד רווח חודשי ₪',0.0,value=15000.0,step=1000.0); need=(fixed+target)/cm2 if cm2 else np.inf
        a,b,c=st.columns(3); a.metric('מחזור נדרש',money(need)); b.metric('ממוצע כיום',money(avg_rev)); c.metric('פער',money(need-avg_rev))
        if need>avg_rev: callout('המשימה',f'לפי ההנחות צריך לסגור פער של {money(need-avg_rev)} במחזור החודשי הממוצע.','amber')
        else: callout('היעד מכוסה',f'לפי ההנחות המחזור הממוצע כבר גבוה בכ־{money(avg_rev-need)} מהנדרש.','green')

# -------------------- DATA --------------------
elif page.startswith('📁'):
    st.markdown('<div class="hero"><div class="level">LEVEL 04 · DATA ROOM</div><h1>חדר הנתונים</h1><p>כאן בודקים על מה אפשר לסמוך ומה עדיין חסר.</p></div>',unsafe_allow_html=True)
    a,b,c=st.columns(3); a.metric('רמת ביטחון',f'{conf_score}%'); b.metric('שורות',len(df)); c.metric('חודשים פעילים',len(active))
    st.markdown(f'<div class="progress-wrap"><div class="progress-fill" style="width:{conf_score}%"></div></div>',unsafe_allow_html=True)
    st.markdown('<div class="section">נתונים מנורמלים</div>',unsafe_allow_html=True)
    st.dataframe(df,use_container_width=True,hide_index=True)
    st.download_button('הורד CSV מנורמל',df.to_csv(index=False).encode('utf-8-sig'),'yatziv_normalized.csv','text/csv',use_container_width=True)
    st.markdown('<div class="section">מה חסר כדי לפתוח יכולות נוספות?</div>',unsafe_allow_html=True)
    c1,c2,c3=st.columns(3)
    with c1: callout('תזרים אמיתי','בנק + כרטיסי אשראי + הלוואות.','blue')
    with c2: callout('עלות מזון אמיתית','מלאי פתיחה/סגירה + קניות.','blue')
    with c3: callout('יעילות עובדים','שעות, תפקידים ותפוקה.','blue')

# -------------------- METHOD --------------------
else:
    st.markdown('<div class="hero"><div class="level">SYSTEM · TRUST LAYER</div><h1>איך YATZIV חושב?</h1><p>מספרים מחושבים במנוע דטרמיניסטי. ההסבר העסקי יושב מעליו.</p></div>',unsafe_allow_html=True)
    a,b,c,d=st.columns(4)
    with a:kpi('ACTUAL','נתון מקור','דוח / קובץ / בנק','good')
    with b:kpi('ASSUMPTION','הנחת משתמש','לתרחיש בלבד','warn')
    with c:kpi('CALCULATED','חישוב','נוסחה מוגדרת','')
    with d:kpi('INSIGHT','הסבר','רק ממה שהנתונים תומכים','')
    st.markdown('<div class="section">סדר העבודה</div>',unsafe_allow_html=True)
    st.markdown('**1. להבין מצב → 2. למצוא שינוי/חריגה → 3. לבדוק סיבה → 4. להריץ החלטה → 5. לראות מה חסר בנתונים.**')
    callout('למה זה חשוב','כך האפליקציה לא הופכת לעוד Dashboard עמוס. כל מסך עונה על שאלה אחת ומוביל לשלב הבא.','green')
    callout('V3 הנוכחית','קריאת PDF אוטומטית עדיין לא פעילה. זה מכוון: קודם מנוע החלטות ומבנה מידע אמינים, אחר כך Parser עם אישור משתמש ו־Confidence לכל שדה.','amber')
