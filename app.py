import streamlit as st
import pandas as pd
import time
from datetime import datetime
from streamlit_autorefresh import st_autorefresh
st.set_page_config(page_title="LUD FS", layout="wide")
st_autorefresh(interval=1000, key="f5")
ss = st.session_state
if 'js' not in ss:
    n = ["Serra","Julian","Omar","Tony","Rochina","Benages","Pedrito","Parre Jr","Baeza","Manu","Pedro Toro","Paco Silla","Jose","Coque","Nacho Gomez"]
    ss.js = [{"n":n[i],"t_t":0.0,"ini":None,"p":False,"g":0,"t":0,"per":0,"rec":0} for i in range(15)]
if 'ml' not in ss: ss.ml, ss.mr, ss.fl, ss.fr, ss.t_a, ss.i_c, ss.run = 0, 0, 0, 0, 0.0, None, False
ah = time.time()
td = ss.t_a + (ah - ss.i_c if ss.run and ss.i_c else 0)
st.markdown("<style>.stApp{background:#f8f9fa}.m-box{background:white;padding:10px;border-radius:10px;text-align:center;box-shadow:0 2px 4px rgba(0,0,0,0.1)}.j-card{background:white;border-radius:8px;padding:5px;margin-bottom:4px;border-left:5px solid #ccc}</style>", unsafe_allow_html=True)
c1, c2, c3 = st.columns([1,4,1])
with c1: st.image("https://upload.wikimedia.org/wikipedia/en/thumb/7/7b/Levante_Uni%C3%B3n_Deportiva%2C_S.A.D._logo.svg/1200px-Levante_Uni%C3%B3n_Deportiva%2C_S.A.D._logo.svg.png", width=50)
with c2: riv = st.text_input("R", "RIVAL", label_visibility="collapsed").upper()
with c3: 
    if st.button("🔄"): ss.clear(); st.rerun()
m1, m2, m3 = st.columns([2,3,2])
with m1:
    st.markdown(f"<div class='m-box'><h3>LUD</h3><h1 style='color:#003D7A'>{ss.ml}</h1><p>F: {ss.fl}</p></div>", unsafe_allow_html=True)
    if st.button("⚽ LUD"): ss.ml+=1; st.rerun()
    if st.button("⚠️ LUD"): ss.fl+=1; st.rerun()
with m2:
    mm, sv = divmod(int(td), 60)
    st.markdown(f"<div class='m-box'><h1 style='font-size:3rem'>{mm:02d}:{sv:02d}</h1></div>", unsafe_allow_html=True)
    if not ss.run:
        if st.button("▶ START"):
            ss.i_c, ss.run = ah, True
            for j in ss.js: 
                if j["p"]: j["ini"] = ah
            st.rerun()
    else:
        if st.button("⏸ STOP"):
            ss.t_a += ah - ss.i_c
            ss.run, ss.i_c = False, None
            for j in ss.js:
                if j["p"] and j["ini"]: j["t_t"] += ah - j["ini"]; j["ini"] = None
            st.rerun()
with m3:
    st.markdown(f"<div class='m-box'><h3>{riv[:6]}</h3><h1 style='color:#7A0019'>{ss.mr}</h1><p>F: {ss.fr}</p></div>", unsafe_allow_html=True)
    if st.button(f"⚽ {riv[:3]}"): ss.mr+=1; st.rerun()
    if st.button(f"⚠️ {riv[:3]}"): ss.fr+=1; st.rerun()
ep = sum(1 for j in ss.js if j["p"])
st.write(f"PISTA: {ep}/5")
cols = st.columns(3)
for i, j in enumerate(ss.js):
    with cols[i % 3]:
        bc = "#003D7A" if j["p"] else "#ccc"
        st.markdown(f"<div class='j-card' style='border-left-color:{bc}'>", unsafe_allow_html=True)
        c_n, c_r = st.columns([2,1])
        j["n"] = c_n.text_input(f"n{i}", j["n"], key=f"in{i}", label_visibility="collapsed")
        tj = j["t_t"] + (ah - j["ini"] if ss.run and j["p"] and j["ini"] else 0)
        mj, sj = divmod(int(tj), 60)
        c_r.markdown(f"<b style='color:{'#2b8a3e' if j['p'] else '#a61e4d'}'>{'🟢' if j['p'] else '🔴'} {mj:02d}:{sj:02d}</b>", unsafe_allow_
