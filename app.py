import streamlit as st
import pandas as pd
import time
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="LUD FS", layout="wide")
st_autorefresh(interval=1000, key="f5")
s = st.session_state

if 'js' not in s:
    n = ["Serra","Julian","Omar","Tony","Rochina","Benages","Pedrito",
         "Parre Jr","Baeza","Manu","Pedro Toro","Paco Silla","Jose",
         "Coque","Nacho Gomez"]
    s.js = [{"n":x,"t":0.0,"i":None,"p":False,"g":0,"s":0,"e":0,"r":0} for x in n]
    s.ml, s.mr, s.fl, s.fr, s.ta, s.ic, s.on = 0, 0, 0, 0, 0.0, None, False

ah = time.time()
td = s.ta + (ah - s.ic if s.on and s.ic else 0)

c1, c2, c3 = st.columns([1,4,1])
with c1: st.image("https://upload.wikimedia.org/wikipedia/en/thumb/7/7b/Levante_Uni%C3%B3n_Deportiva%2C_S.A.D._logo.svg/1200px-Levante_Uni%C3%B3n_Deportiva%2C_S.A.D._logo.svg.png", width=50)
with c2: rv = st.text_input("R", "RIVAL", label_visibility="collapsed").upper()
with c3: 
    if st.button("🔄"): s.clear(); st.rerun()

m1, m2, m3 = st.columns([2,3,2])
with m1:
    st.metric("LUD", s.ml, f"Faltas: {s.fl}")
    if st.button("⚽ GOL", key="gl"): s.ml+=1; st.rerun()
    if st.button("⚠️ FAL", key="fl"): s.fl+=1; st.rerun()
with m2:
    mm, sv = divmod(int(td), 60)
    st.markdown(f"<h1 style='text-align:center;'>{mm:02d}:{sv:02d}</h1>", 1)
    if not s.on:
        if st.button("▶ START", type="primary", use_container_width=1):
            s.ic, s.on = ah, True
            for j in s.js: 
                if j["p"]: j["i"] = ah
            st.rerun()
    else:
        if st.button("⏸ STOP", type="secondary", use_container_width=1):
            s.ta += ah - s.ic
            s.on, s.ic = False, None
            for j in s.js:
                if j["p"] and j["i"]: j["t"] += ah - j["i"]; j["i"] = None
            st.rerun()
with m3:
    st.metric(rv[:5], s.mr, f"Faltas: {s.fr}")
    if st.button("⚽ GOL ", key="gr"): s.mr+=1; st.rerun()
    if st.button("⚠️ FAL ", key="fr"): s.fr+=1; st.rerun()

st.divider()
ep = sum(1 for j in s.js if j["p"])
st.write(f"Pista: {ep}/5")
cols = st.columns(3)
for idx, j in enumerate(s.js):
    with cols[idx % 3]:
        with st.container(border=True):
            cn, cr = st.columns([1.5, 1])
            j["n"] = cn.text_input(f"n{idx}", j["n"], key=f"in{idx}", label_visibility="collapsed")
            tt = j["t"] + (ah - j["i"] if s.on and j["p"] and j["i"] else 0)
            m_j, s_j = divmod(int(tt), 60)
            cr.write(f"{'🟢' if j['p'] else '🔴'} {m_j:02d}:{s_j:02d}")
            s1,s2,s3,s4,s5 = st.columns(5)
            if s1.button("🎯", key=f"s1{idx}"): j["s"]+=1
            if s2.button("🛡️", key=f"s2{idx}"): j["r"]+=1
            if s3.button("❌", key=f"s3{idx}"): j["e"]+=1
            if s4.button("⚽", key=f"s4{idx}"): j["g"]+=1; s.ml+=1; st.rerun()
            if s5.button("
