import streamlit as st
import pandas as pd
import time
from datetime import datetime
from streamlit_autorefresh import st_autorefresh
st.set_page_config(page_title="LUD PRO", layout="wide")
st_autorefresh(interval=1000, key="f5")
ss = st.session_state
st.markdown("""<style>.stApp{background:#F0F2F6}.h-box{background:linear-gradient(90deg,#003D7A,#7A0019);padding:10px;border-radius:10px;color:white;text-align:center}.rel-box{background:#1E1E1E;border:3px solid #FFD700;border-radius:20px;padding:10px}.rel-txt{color:white;font-size:4rem!important;font-weight:bold;text-align:center;margin:0}.m-card{padding:15px;border-radius:15px;color:white;text-align:center;min-height:180px}.stButton>button{height:3rem;font-weight:bold}.j-card{background:white;padding:8px;border-radius:10px;border-left:8px solid #D3D3D3;margin-bottom:5px}</style>""", unsafe_allow_html=True)
if 'js' not in ss: ss.js = [{"id":i,"n":f"J{i+1}","t1":0.0,"t2":0.0,"ini":None,"p":False,"g":0,"t":0,"per":0,"rec":0} for i in range(14)]
if 'rt1' not in ss: ss.rt1,ss.rt2,ss.pt,ss.ml,ss.mr,ss.fl,ss.fr = 0.0,0.0,"T1",0,0,0,0
if 'ac' not in ss: ss.ac,ss.ig,ss.pos = False,None,"NEU"
if 'tpl' not in ss: ss.tpl,ss.tpr,ss.tpn,ss.lpc = 0.0,0.0,0.0,time.time()
now = time.time()
if ss.ac:
    d = now - ss.lpc
    if ss.pos == "LUD": ss.tpl += d
    elif ss.pos == "RIV": ss.tpr += d
    else: ss.tpn += d
ss.lpc = now
cl, ci, cr = st.columns([1, 4, 1])
cl.image("https://upload.wikimedia.org/wikipedia/en/thumb/7/7b/Levante_Uni%C3%B3n_Deportiva%2C_S.A.D._logo.svg/1200px-Levante_Uni%C3%B3n_Deportiva%2C_S.A.D._logo.svg.png", width=60)
with ci:
    r1, r2 = st.columns(2)
    rvn = r1.text_input("R", "RIVAL", label_visibility="collapsed").upper()
    fp = r2.date_input("F", datetime.now(), label_visibility="collapsed")
    st.markdown(f"<div class='h-box'><h2>LUD vs {rvn}</h2></div>", unsafe_allow_html=True)
if cr.button("RESET"): ss.clear(); st.rerun()
c1, c2, c3 = st.columns([2, 3, 2])
with c1:
    st.markdown(f"<div class='m-card' style='background:{'#FF0000' if ss.fl>=5 else '#003D7A'}'><h3>LUD</h3><h1>{ss.ml}</h1><p>F: {ss.fl}</p></div>", unsafe_allow_html=True)
    la,lb=st.columns(2)
    if la.button("⚽",key="gl"):ss.ml+=1;st.rerun()
    if lb.button("⚠️",key="fl"):ss.fl+=1;st.rerun()
with c2:
    tv=ss.rt1 if ss.pt=="T1" else ss.rt2
    if ss.ac and ss.ig:tv+=now-ss.ig
    m,s=divmod(int(tv),60)
    st.markdown(f"<div class='rel-box'><p class='rel-txt'>{m:02d}:{s:02d}</p></div>", unsafe_allow_html=True)
    a1,a2,a3=st.columns(3)
    if a1.button("-1s"):
        if ss.pt=="T1":ss.rt1-=1
        else:ss.rt2-=1
    if a2.button("▶/⏸"):
        if not ss.ac:
            ss.ac,ss
