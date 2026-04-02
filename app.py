import streamlit as st
import pandas as pd
import time
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="LUD v2.1", layout="wide")
st_autorefresh(interval=1000, key="f5")
s = st.session_state

if 'js' not in s:
    n = ["Serra","Julian","Omar","Tony","Rochina","Benages","Pedrito","Parre Jr","Baeza","Manu","Pedro Toro","Paco Silla","Jose","Coque","Nacho Gomez"]
    s.js = [{"n":x,"t":0.0,"i":None,"p":False,"g":0,"s":0,"e":0,"r":0} for x in n]
    s.ml,s.mr,s.fl,s.fr,s.ta,s.ic,s.on = 0,0,0,0,0.0,None,False

ah = time.time()
tr = s.ta + (ah - s.ic if s.on and s.ic else 0)
rem = max(0, 1200 - tr)

c1, c2 = st.columns([4,1])
with c1:
    ci, ct = st.columns([0.5, 3.5])
    ci.image("https://upload.wikimedia.org/wikipedia/en/thumb/7/7b/Levante_Uni%C3%B3n_Deportiva%2C_S.A.D._logo.svg/200px-Levante_Uni%C3%B3n_Deportiva%2C_S.A.D._logo.svg.png", width=60)
    rv = ct.text_input("R", "RIVAL", label_visibility="collapsed").upper()
if c2.button("🔄"): s.clear(); st.rerun()

m1, m2, m3 = st.columns([2,3,2])
with m1:
    st.metric("LUD", s.ml, f"F: {s.fl}")
    if st.button("⚽ LUD", use_container_width=1): s.ml+=1; st.rerun()
    f1, f2 = st.columns(2)
    if f1.button("F+", key="flp"): s.fl+=1; st.rerun()
    if f2.button("F-", key="flm"): s.fl=max(0, s.fl-1); st.rerun()
with m2:
    mm, sv = divmod(int(rem), 60)
    st.markdown(f"<h1 style='text-align:center;font-size:4rem;color:red;'>{mm:02d}:{sv:02d}</h1>", 1)
    if not s.on:
        if st.button("▶ START", use_container_width=1):
            s.ic, s.on = ah, True
            for j in s.js: 
                if j["p"]: j["i"] = ah
            st.rerun()
    else:
        if st.button("⏸ STOP", use_container_width=1):
            s.ta += ah - s.ic
            s.on, s.ic = False, None
            for j in s.js:
                if j["p"] and j["i"]: j["t"]+=ah-j["i"]; j["i"]=None
            st.rerun()
with m3:
    st.metric(rv[:5], s.mr, f"F: {s.fr}")
    if st.button(f"⚽ {rv[:3]}", use_container_width=1): s.mr+=1; st.rerun()
    r1, r2 = st.columns(2)
    if r1.button("F+", key="frp"): s.fr+=1; st.rerun()
    if r2.button("F-", key="frm"): s.fr=max(0, s.fr-1); st.rerun()

st.divider()
st.subheader("📊 MONITOR")
res = []
for j in s.js:
    tt = j["t"] + (ah - j["i"] if s.on and j["p"] and j["i"] else 0)
    m_j, s_
