import streamlit as st
import pandas as pd
import time
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="LUD", layout="wide")
st_autorefresh(interval=1000, key="f5")
s = st.session_state

if 'js' not in s:
    n = ["Serra","Julian","Omar","Tony","Rochina","Benages","Pedrito","Parre Jr","Baeza","Manu","Pedro Toro","Paco Silla","Jose","Coque","Nacho Gomez"]
    s.js = [{"n":x,"t":0.0,"i":None,"p":False,"g":0,"s":0,"e":0,"r":0} for x in n]
    s.ml, s.mr, s.ta, s.ic, s.on = 0, 0, 0.0, None, False

ah = time.time()
td = s.ta + (ah - s.ic if s.on and s.ic else 0)

# CABECERA
c1, c2 = st.columns([4,1])
rv = c1.text_input("RIVAL", "RIVAL").upper()
if c2.button("RESET"): s.clear(); st.rerun()

# MARCADOR
m1, m2, m3 = st.columns(3)
m1.metric("LUD", s.ml)
if m1.button("⚽ GOL LUD"): s.ml+=1; st.rerun()

mm, sv = divmod(int(td), 60)
m2.markdown(f"<h1 style='text-align:center;'>{mm:02d}:{sv:02d}</h1>", unsafe_allow_html=True)
if not s.on:
    if m2.button("▶ START", use_container_width=True):
        s.ic, s.on = ah, True
        for j in s.js: 
            if j["p"]: j["i"] = ah
        st.rerun()
else:
    if m2.button("⏸ STOP", use_container_width=True):
        s.ta += ah - s.ic
        s.on, s.ic = False, None
        for j in s.js:
            if j["p"] and j["i"]: j["t"] += ah - j["i"]; j["i"] = None
        st.rerun()

m3.metric(rv[:8], s.mr)
if m3.button(f"⚽ GOL {rv[:3]}"): s.mr+=1; st.rerun()

# JUGADORES
st.divider()
cols = st.columns(3)
for idx, j in enumerate(s.js):
    with cols[idx % 3]:
        with st.container(border=True):
            st.write(f"{'🟢' if j['p'] else '🔴'} **{j['n']}**")
            
            # Scouting rapido
            c_s1, c_s2, c_s3, c_s4 = st.columns(4)
            if c_s1.button("🎯", key=f"t{idx}"): j["s"]+=1
            if c_s2.button("🛡️", key=f"r{idx}"): j["r"]+=1
            if c_s3.button("❌", key=f"e{idx}"): j["e"]+=1
            if c_s4.button("⚽", key=f"g{idx}"): j["g"]+=1; s.ml+=1; st.rerun()
            
            # Cambio
            if st.button("CAMBIO PISTA/BANCO", key=f"c{idx}", use_container_width=True):
                if not j["p"] and sum(1 for x in s.js if x["p"]) < 5:
                    j["p"], j["i"] = True, (ah if s.on else None)
                elif j["p"]:
                    if s.on and j["i"]: j["t"] += ah - j["i"]
                    j["p"], j["i"] = False, None
                st.rerun()

if st.button("💾 DESCARGAR CSV"):
    st.download_button("BAJAR", pd.DataFrame(s.js).to_csv().encode('utf-8'), "LUD.csv")
