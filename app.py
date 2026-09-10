from __future__ import annotations
from datetime import datetime
from pathlib import Path
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import streamlit as st

from utils.metrics import evaluate_model, model_config
from utils.prediction import ArtifactLoadError, compute_feature_baseline, load_artifacts, predict, tree_votes
from utils.preprocessing import DEMO_PRESETS, FEATURE_COLUMNS, FEATURE_DESCRIPTIONS, PROTOCOL_OPTIONS, TARGET_COLUMN, build_input_row

BASE_DIR = Path(__file__).parent
st.set_page_config(page_title="Sentinel IDS | Network Security", page_icon="🛡️", layout="wide", initial_sidebar_state="expanded")

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500;700&display=swap');
:root{--bg:#070b12;--panel:#0d1420;--panel2:#111b29;--line:#203047;--text:#e7edf7;--muted:#8b9ab0;--cyan:#22d3ee;--green:#34d399;--red:#fb7185;--amber:#fbbf24}
.stApp{background:radial-gradient(circle at 80% -10%,rgba(34,211,238,.10),transparent 32%),radial-gradient(circle at -10% 40%,rgba(59,130,246,.08),transparent 28%),var(--bg);font-family:Inter,sans-serif;color:var(--text)}
[data-testid="stSidebar"]{background:#080d15;border-right:1px solid #182538}
.block-container{padding:1.5rem 2.4rem 3rem;max-width:1450px}
.hero{padding:24px 28px;border:1px solid #203047;border-radius:22px;background:linear-gradient(135deg,rgba(17,27,41,.96),rgba(8,13,22,.96));box-shadow:0 20px 60px rgba(0,0,0,.22);margin-bottom:22px}
.hero-row{display:flex;justify-content:space-between;gap:20px;align-items:flex-start}.brand{font-size:13px;font-weight:800;letter-spacing:3px;color:#fff}.brand span{color:var(--cyan)}
.eyebrow{font-size:11px;letter-spacing:2px;color:var(--cyan);font-weight:800;margin-top:20px}.hero h1{font-size:38px;line-height:1.1;margin:7px 0;color:#fff}.desc{color:var(--muted);max-width:850px;font-size:14px}
.pills{display:flex;gap:8px;flex-wrap:wrap;justify-content:flex-end}.pill{padding:7px 11px;border:1px solid #26364d;border-radius:999px;color:#b8c5d8;font:600 10px 'JetBrains Mono'}.online{color:#6ee7b7;border-color:#1c604d;background:rgba(52,211,153,.06)}
.card{background:linear-gradient(145deg,rgba(15,23,36,.95),rgba(10,16,26,.95));border:1px solid #1e3048;border-radius:18px;padding:19px;min-height:100%;box-shadow:0 12px 35px rgba(0,0,0,.12)}
.card h3{margin:0 0 6px;font-size:15px}.muted{color:var(--muted);font-size:12px}.big{font-size:29px;font-weight:800;margin:6px 0}.mono{font-family:'JetBrains Mono';}.accent{color:var(--cyan)}.good{color:var(--green)}.bad{color:var(--red)}.warn{color:var(--amber)}
.kpi{padding:18px;border:1px solid #1e3048;border-radius:16px;background:rgba(12,19,30,.78)}.kpi .label{color:#8fa0b7;font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:1px}.kpi .value{font-size:27px;font-weight:800;margin-top:5px}.kpi .sub{font-size:11px;color:#64748b;margin-top:3px}
.section{font-size:12px;font-weight:800;letter-spacing:1.4px;text-transform:uppercase;color:#9fb0c6;margin:5px 0 12px}.flow{display:flex;gap:8px;align-items:center;flex-wrap:wrap}.step{flex:1;min-width:120px;text-align:center;padding:14px 8px;border:1px solid #23344c;border-radius:12px;background:#0c1522}.step b{display:block;color:#22d3ee;font-size:10px;margin-bottom:4px}.step span{font-size:12px;font-weight:700}.arrow{color:#40526a}
.explain{padding:16px;border-radius:14px;background:rgba(34,211,238,.04);border:1px solid rgba(34,211,238,.16);color:#b8c7da;font-size:13px;line-height:1.65}.explain strong{color:#fff}
.result{padding:28px;border-radius:18px;text-align:center;border:1px solid}.normal{background:rgba(6,44,31,.55);border-color:#236c52}.attack{background:rgba(65,12,22,.6);border-color:#7d3042}.result-title{font-size:26px;font-weight:800}.result-number{font:800 38px 'JetBrains Mono';margin:5px 0}
.badge{display:inline-block;padding:5px 10px;border-radius:999px;font:700 11px 'JetBrains Mono';border:1px solid}.high{color:#fda4af;background:rgba(251,113,133,.1);border-color:#7d3042}.medium{color:#fcd34d;background:rgba(251,191,36,.08);border-color:#6d5415}.none{color:#6ee7b7;background:rgba(52,211,153,.08);border-color:#236c52}
.smallcap{font-size:10px;letter-spacing:1px;text-transform:uppercase;color:#64748b;font-weight:800}.footer{color:#526277;font-size:11px;text-align:center;padding:25px 0}
div[data-testid="stMetric"]{background:#0d1420;border:1px solid #1e3048;padding:12px;border-radius:14px}
button[kind="primary"]{background:linear-gradient(90deg,#0891b2,#2563eb)!important;border:0!important}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

@st.cache_resource(show_spinner=False)
def load(): return load_artifacts(BASE_DIR)
try:
    artifacts=load(); model,data=artifacts.model,artifacts.data; error=None
except ArtifactLoadError as e: model=data=None; error=str(e)

if not hasattr(st.session_state,'events'): st.session_state.events=[]
if not hasattr(st.session_state,'last_result'): st.session_state.last_result=None

if model is None or data is None:
    st.error(error or 'Required files are missing.'); st.stop()

baseline=compute_feature_baseline(data); evaluation=evaluate_model(model,data); meta=model_config(model)

def hero(kicker,title,desc):
    st.markdown(f'''<div class="hero"><div class="hero-row"><div><div class="brand">🛡 <span>SENTINEL</span> IDS</div><div class="eyebrow">{kicker}</div><h1>{title}</h1><div class="desc">{desc}</div></div><div class="pills"><span class="pill online">● ENGINE READY</span><span class="pill">RANDOM FOREST</span><span class="pill">DEMO DATASET</span></div></div></div>''',unsafe_allow_html=True)

def card(title,body): st.markdown(f'<div class="card"><h3>{title}</h3>{body}</div>',unsafe_allow_html=True)

def kpi(label,value,sub=''): return f'<div class="kpi"><div class="label">{label}</div><div class="value">{value}</div><div class="sub">{sub}</div></div>'

def flow(items):
    html='<div class="flow">'
    for i,x in enumerate(items): html+=f'<div class="step"><b>0{i+1}</b><span>{x}</span></div>'+('<div class="arrow">→</div>' if i<len(items)-1 else '')
    st.markdown(html+'</div>',unsafe_allow_html=True)

def nav():
    with st.sidebar:
        st.markdown('<div class="brand" style="font-size:16px">🛡 <span>SENTINEL</span> IDS</div><div class="muted" style="margin:6px 0 20px">Network threat detection platform</div>',unsafe_allow_html=True)
        page=st.radio('WORKSPACE',['Command Center','Traffic Analyzer','Incident Console','AI Explainability','Model Lab','Dataset Intelligence','Architecture'],label_visibility='visible')
        st.divider(); st.markdown('**ENGINE STATUS**')
        st.markdown('<span class="good">●</span> Model loaded<br><span class="good">●</span> Dataset loaded<br><span class="good">●</span> Prediction ready',unsafe_allow_html=True)
        st.divider(); st.caption(f'Last session check · {datetime.now().strftime("%H:%M:%S")}')
        st.caption('Academic project • Safe demonstration environment')
    return page

page=nav()

if page=='Command Center':
    hero('SECURITY OPERATIONS','See the network. Understand the threat.','Sentinel turns traffic features into an interpretable security decision using a trained Random Forest model.')
    total=len(data); attacks=int(data[TARGET_COLUMN].sum()); normal=total-attacks
    c=st.columns(4)
    for col,html in zip(c,[kpi('Traffic records',f'{total:,}','synthetic demonstration data'),kpi('Normal traffic',f'{normal:,}',f'{normal/total:.1%} of dataset'),kpi('Intrusion samples',f'{attacks:,}',f'{attacks/total:.1%} of dataset'),kpi('Model F1',f'{evaluation.f1:.1%}','evaluation on demo data')]): col.markdown(html,unsafe_allow_html=True)
    st.write('')
    a,b=st.columns([1.35,1])
    with a:
        st.markdown('<div class="card"><div class="section">How Sentinel works</div>',unsafe_allow_html=True)
        st.markdown('<div class="explain"><strong>Think of the model as a security committee.</strong> Each decision tree examines the same connection from a slightly different perspective. The forest combines those votes and produces one final classification.</div><br>',unsafe_allow_html=True)
        flow(['Traffic record','Features','Decision trees','Majority vote','Risk decision'])
        st.markdown('</div>',unsafe_allow_html=True)
    with b:
        labels=['Normal','Intrusion']; vals=[normal,attacks]
        fig=go.Figure(go.Pie(labels=labels,values=vals,hole=.62,textinfo='percent',marker=dict(colors=['#34d399','#fb7185'])))
        fig.update_layout(height=300,paper_bgcolor='rgba(0,0,0,0)',font=dict(color='#cbd5e1'),margin=dict(l=0,r=0,t=25,b=0),showlegend=True)
        st.markdown('<div class="card"><div class="section">Dataset threat mix</div>',unsafe_allow_html=True); st.plotly_chart(fig,use_container_width=True,config={'displayModeBar':False}); st.markdown('</div>',unsafe_allow_html=True)
    st.write('')
    card('Why this project matters','<div class="explain"><strong>IDS = an early-warning layer.</strong><br>Instead of manually inspecting thousands of connections, an ML model learns patterns from labeled examples and flags traffic that looks suspicious. Sentinel then exposes the evidence and confidence so a human can investigate.</div>')

elif page=='Traffic Analyzer':
    hero('INTERACTIVE DETECTION','Traffic Analyzer','Test a connection, watch the ML pipeline run, and inspect why the model produced its decision.')
    left,right=st.columns([1,1])
    with left:
        st.markdown('<div class="card"><div class="section">1 · Build a traffic record</div>',unsafe_allow_html=True)
        p1,p2=st.columns(2)
        if p1.button('🟢 Load normal preset',use_container_width=True):
            for k,v in DEMO_PRESETS['Normal Traffic'].items(): st.session_state[f'x_{k}']=v
        if p2.button('🔴 Load attack-like preset',use_container_width=True):
            for k,v in DEMO_PRESETS['Attack Traffic'].items(): st.session_state[f'x_{k}']=v
        protocol=st.selectbox('Protocol',PROTOCOL_OPTIONS,index=0,key='x_protocol'); duration=st.number_input('Duration (seconds)',0.,10000.,10.,key='x_duration'); src=st.number_input('Source bytes',0,10000000,1200,key='x_src_bytes'); dst=st.number_input('Destination bytes',0,10000000,4500,key='x_dst_bytes'); packets=st.number_input('Packets',1,100000,25,key='x_packets'); sp=st.number_input('Source port',0,65535,443,key='x_src_port'); dp=st.number_input('Destination port',0,65535,80,key='x_dst_port'); failed=st.number_input('Failed logins',0,100,0,key='x_failed_logins')
        if st.button('🔍 ANALYZE TRAFFIC',type='primary',use_container_width=True):
            row=build_input_row(duration,protocol,src,dst,packets,sp,dp,failed); result=predict(model,baseline,row); st.session_state.last_result=result
            st.session_state.events.insert(0,{'Time':datetime.now().strftime('%H:%M:%S'),'Protocol':protocol,'Prediction':result.label,'Risk':result.risk_level,'Confidence':f'{result.confidence:.1%}'})
        st.markdown('</div>',unsafe_allow_html=True)
    with right:
        result=st.session_state.last_result
        st.markdown('<div class="card"><div class="section">2 · Model decision</div>',unsafe_allow_html=True)
        if result is None:
            st.markdown('<div class="explain"><strong>Ready.</strong><br>Load a preset or enter your own traffic characteristics, then run the detector.</div>',unsafe_allow_html=True)
        else:
            cls='attack' if result.prediction else 'normal'; badge='high' if result.risk_level=='HIGH' else 'medium' if result.risk_level=='MEDIUM' else 'none'
            title='🚨 INTRUSION DETECTED' if result.prediction else '🟢 NORMAL TRAFFIC'
            st.markdown(f'<div class="result {cls}"><div class="smallcap">Random Forest classification</div><div class="result-title">{title}</div><div class="result-number">{result.confidence:.1%}</div><div class="smallcap">Prediction confidence · not model accuracy</div><span class="badge {badge}">RISK · {result.risk_level}</span></div>',unsafe_allow_html=True)
            fig=go.Figure(go.Bar(x=[result.prob_normal,result.prob_attack],y=['Normal','Intrusion'],orientation='h',marker_color=['#34d399','#fb7185'],text=[f'{result.prob_normal:.1%}',f'{result.prob_attack:.1%}'],textposition='auto'))
            fig.update_layout(height=210,xaxis=dict(range=[0,1],tickformat='.0%',showgrid=False),yaxis=dict(showgrid=False),paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)',font=dict(color='#cbd5e1'),margin=dict(l=10,r=20,t=20,b=10))
            st.plotly_chart(fig,use_container_width=True,config={'displayModeBar':False})
            if result.indicators:
                st.markdown('**Indicators supported by the submitted record**')
                for x in result.indicators: st.markdown(f'✓ {x}')
        st.markdown('</div>',unsafe_allow_html=True)

elif page=='Incident Console':
    hero('SECURITY EVENTS','Incident Console','A lightweight event layer turns individual model predictions into a reviewable security trail.')
    if st.session_state.events:
        df=pd.DataFrame(st.session_state.events)
        c=st.columns(4); c[0].markdown(kpi('Events',len(df)),unsafe_allow_html=True); c[1].markdown(kpi('High risk',sum(df.Risk=='HIGH')),unsafe_allow_html=True); c[2].markdown(kpi('Intrusions',sum(df.Prediction=='INTRUSION DETECTED')),unsafe_allow_html=True); c[3].markdown(kpi('Latest',df.iloc[0].Time),unsafe_allow_html=True)
        st.write(''); st.dataframe(df,use_container_width=True,hide_index=True)
    else: card('No events yet','<div class="explain">Run a few records in <strong>Traffic Analyzer</strong>. Each prediction becomes a local demonstration event here.</div>')
    card('How this scales','<div class="explain">For a production system, this event layer could feed a message queue, SIEM, database, alerting service, and analyst workflow. This project intentionally keeps the response local and safe.</div>')

elif page=='AI Explainability':
    hero('MODEL INTERPRETABILITY','AI Explainability','Open the black box: inspect feature importance and the actual votes produced by individual Random Forest trees.')
    imp=pd.Series(model.feature_importances_,index=FEATURE_COLUMNS).sort_values()
    fig=go.Figure(go.Bar(x=imp.values,y=imp.index,orientation='h',marker_color='#22d3ee'))
    fig.update_layout(height=380,paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)',font=dict(color='#cbd5e1'),xaxis=dict(showgrid=False),yaxis=dict(showgrid=False),margin=dict(l=10,r=20,t=20,b=20))
    a,b=st.columns([1.2,1])
    with a:
        st.markdown('<div class="card"><div class="section">Feature importance</div>',unsafe_allow_html=True); st.plotly_chart(fig,use_container_width=True,config={'displayModeBar':False}); st.markdown('</div>',unsafe_allow_html=True)
    with b:
        choice=st.radio('Inspect real tree votes',list(DEMO_PRESETS.keys()),horizontal=True); row=build_input_row(**DEMO_PRESETS[choice]); votes=tree_votes(model,row,limit=min(20,meta['n_estimators'])); attack=sum(votes); normal_votes=len(votes)-attack
        st.markdown(f'<div class="card"><div class="section">Ensemble vote</div><div class="big accent">{attack} / {len(votes)} attack votes</div><div class="muted">{normal_votes} trees voted normal. These are actual predictions from sampled estimators in the loaded model.</div><br>',unsafe_allow_html=True)
        cols=st.columns(5)
        for i,v in enumerate(votes): cols[i%5].markdown(f'<div class="kpi"><div class="label">TREE {i+1}</div><div class="value {"bad" if v else "good"}">{"ATTACK" if v else "NORMAL"}</div></div>',unsafe_allow_html=True)
        st.markdown('</div>',unsafe_allow_html=True)
    st.write(''); card('The concept in one sentence','<div class="explain"><strong>Random Forest is an ensemble:</strong> many decision trees make independent predictions, then the forest combines their votes to reduce dependence on any single tree.</div>')

elif page=='Model Lab':
    hero('MACHINE LEARNING','Model Lab','Evaluation, configuration, and failure modes — the part of the project an interviewer will care about.')
    c=st.columns(4)
    for col,name,val in zip(c,['Accuracy','Precision','Recall','F1 Score'],[evaluation.accuracy,evaluation.precision,evaluation.recall,evaluation.f1]): col.markdown(kpi(name,f'{val:.2%}','demo dataset evaluation'),unsafe_allow_html=True)
    st.write('')
    a,b=st.columns(2)
    with a:
        cm=evaluation.confusion; fig=go.Figure(go.Heatmap(z=cm,x=['Predicted Normal','Predicted Intrusion'],y=['Actual Normal','Actual Intrusion'],text=cm,texttemplate='%{text}',colorscale=[[0,'#101827'],[1,'#22d3ee']],showscale=False)); fig.update_layout(height=320,paper_bgcolor='rgba(0,0,0,0)',font=dict(color='#cbd5e1'),margin=dict(l=10,r=10,t=30,b=10)); st.markdown('<div class="card"><div class="section">Confusion matrix</div>',unsafe_allow_html=True); st.plotly_chart(fig,use_container_width=True,config={'displayModeBar':False}); st.markdown('</div>',unsafe_allow_html=True)
    with b:
        card('Configuration',f'<div class="explain"><strong>Trees:</strong> {meta["n_estimators"]}<br><strong>Max depth:</strong> {meta["max_depth"]}<br><strong>Criterion:</strong> {meta["criterion"]}<br><strong>Class weighting:</strong> {meta["class_weight"]}<br><strong>Test split used during training:</strong> 20%</div>')
    st.warning('Important: the included dataset is synthetic and these metrics are not evidence of real-world IDS performance. A stronger next version would train and validate on a public benchmark such as CIC-IDS2017 or UNSW-NB15.')

elif page=='Dataset Intelligence':
    hero('DATA SCIENCE','Dataset Intelligence','Understand what the model sees before asking what the model predicts.')
    st.dataframe(data.head(25),use_container_width=True,hide_index=True)
    a,b=st.columns(2)
    with a:
        counts=data[TARGET_COLUMN].value_counts().sort_index(); fig=go.Figure(go.Bar(x=['Normal','Intrusion'],y=[counts.get(0,0),counts.get(1,0)],marker_color=['#34d399','#fb7185'],text=[counts.get(0,0),counts.get(1,0)],textposition='auto')); fig.update_layout(height=300,paper_bgcolor='rgba(0,0,0,0)',font=dict(color='#cbd5e1'),yaxis=dict(showgrid=False)); st.markdown('<div class="card"><div class="section">Class distribution</div>',unsafe_allow_html=True); st.plotly_chart(fig,use_container_width=True,config={'displayModeBar':False}); st.markdown('</div>',unsafe_allow_html=True)
    with b:
        rows=''.join(f'<tr><td>{x}</td><td>{FEATURE_DESCRIPTIONS[x]}</td></tr>' for x in FEATURE_COLUMNS); st.markdown(f'<div class="card"><div class="section">Feature dictionary</div><table style="width:100%;font-size:12px;color:#b9c6d8"><tr><th align="left">Feature</th><th align="left">Meaning</th></tr>{rows}</table></div>',unsafe_allow_html=True)

elif page=='Architecture':
    hero('SYSTEM DESIGN','From Experiment to Engineering Project','The ML classifier is one component. The surrounding pipeline makes Sentinel useful, explainable, and extensible.')
    flow(['Traffic source','Feature extraction','Validation','Random Forest','Risk scoring','Event console'])
    st.write('')
    a,b,c=st.columns(3)
    a.markdown(kpi('Frontend','Streamlit','interactive security console'),unsafe_allow_html=True)
    b.markdown(kpi('ML engine','Scikit-learn','Random Forest classifier'),unsafe_allow_html=True)
    c.markdown(kpi('Data layer','Pandas + CSV','demo traffic dataset'),unsafe_allow_html=True)
    st.write(''); card('Engineering roadmap','<div class="explain"><strong>Phase 1 — Current:</strong> synthetic labeled traffic + ML classifier + interactive analysis.<br><strong>Phase 2:</strong> public benchmark dataset, cross-validation, model comparison, calibration.<br><strong>Phase 3:</strong> safe packet-feature ingestion, persistent event store, analyst alerts.<br><strong>Phase 4:</strong> deployment, authentication, monitoring, drift detection, and reproducible evaluation.</div>')
    card('Resume-ready positioning','<div class="explain"><strong>Do not pitch this as “just an experiment.”</strong> Pitch it as an ML security analytics platform where the lab requirement became the first version of a larger engineering system.</div>')

st.markdown('<div class="footer">SENTINEL IDS · Intelligent Network Threat Detection · Educational / demonstration environment</div>',unsafe_allow_html=True)
