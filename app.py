import streamlit as st
import pandas as pd
import time
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="LUD FS - Fatiga V1.2", layout="wide")
st_autorefresh(interval=1000, key="f5")
s = st.session_state

st.markdown("<h1 style='text-align:center;'>Control de Tiempos y Fatiga</h1>", 1)

if 'js' not in s:
    n = ["Serra","Julian","Omar","Tony","Rochina","Benages","Pedrito","Parre Jr","Baeza","Manu","Pedro Toro","Paco Silla","Jose","Coque","Nacho Gomez"]
    s.js = [{"n":x,"t":0.0,"i":None,"p":False,"g":0,"s":0,"e":0,"r":0} for x in n]
    s.ml, s.mr, s.ta, s.ic, s.on = 0, 0, 0.0, None, False

ah = time.time()
td = s.ta + (ah - s.ic if s.on and s.ic else 0)

c1, c2 = st.columns([4,1])
rv = c1.text_input("RIVAL", "RIVAL").upper()
if c2.button("RESET"): s.clear(); st.rerun()

m1, m2, m3 = st.columns(3)
m1.metric("LUD", s.ml)
if m1.button("⚽ GOL LUD"): s.ml+=1; st.rerun()

mm, sv = divmod(int(td), 60)
m2.markdown(f"<h1 style='text-align:center; font-size:3.5rem;'>{mm:02d}:{sv:02d}</h1>", 1)
if not s.on:
    if m2.button("▶ START", use_container_width=1):
        s.ic, s.on = ah, True
        for j in s.js: 
            if j["p"]: j["i"] = ah
        st.rerun()
else:
    if m2.button("⏸ STOP", use_container_width=1):
        s.ta += ah - s.ic
        s.on, s.ic = False, None
        for j in s.js:
            if j["p"] and j["i"]: j["t"] += ah - j["i"]; j["i"] = None
        st.rerun()

m3.metric(rv[:8], s.mr)
if m3.button(f"⚽ GOL {rv[:3]}"): s.mr+=1; st.rerun()

st.divider()
ep = sum(1 for x in s.js if x["p"])
st.subheader(f"🏃 PISTA: {ep} / 5")

cols = st.columns(3)
for idx, j in enumerate(s.js):
    with cols[idx % 3]:
        with st.container(border=True):
            tt = j["t"] + (ah - j["i"] if s.on and j["p"] and j["i"] else 0)
            mj, sj = divmod(int(tt), 60)
            mins = tt / 60.0
            
            # Lógica de Color y Texto de Fatiga
            if mins <= 3: 
                col, txt = "#2ecc71", "BAJA" # Verde
            elif mins <= 5: 
                col, txt = "#f39c12", "MEDIA" # Naranja
            else: 
                col, txt = "#e74c3c", "ALTA" # Rojo
            
            c_n, c_t = st.columns([1.5, 1])
            c_n.write(f"{'🟢' if j['p'] else '🔴'} **{j['n']}**")
            c_t.write(f"⏱️ **{mj:02d}:{sj:02d}**")
            
            # BARRA DE FATIGA MEJORADA
            ancho = min((mins / 7.0) * 100, 100) # El 100% de la barra son 7 mins
            st.markdown(f"""
                <div style="border: 1px solid #ddd; border-radius: 5px; background: #eee; height: 15px; width: 100%;">
                    <div style="background-color: {col}; width: {ancho}%; height: 100%; border-radius: 4px; transition: width 0.5s;">
                    </div>
                </div>
                <p style="margin:0; font-size: 10px; color: {col}; font-weight: bold; text-align: right;">FATIGA: {txt}</p>
                """, unsafe_allow_html=True)
            
            s1, s2, s3, s4 = st.columns(4)
            if s1.button("🎯", key=f"t{idx}"): j["s"]+=1
            if s2.button("🛡️", key=f"r{idx}"): j["r"]+=1
            if s3.button("❌", key=f"e{idx}"): j["e"]+=1
            if s4.button("⚽", key=f"g{idx}"): j["g"]+=1; s.ml+=1; st.rerun()
            
            bt = "SALIR" if j["p"] else "ENTRAR"
            if st.button(bt, key=f"c{idx}", use_container_width=1):
                if not j["p"] and ep < 5:
                    j["p"], j["i"] = True, (ah if s.on else None)
                elif j["p"]:
                    if s.on and j["i"]: j["t"] += ah - j["i"]
                    j["p"], j["i"] = False, None
                st.rerun()

st.divider()
if st.button("💾 DESCARGAR RESULTADOS"):
    st.download_button("BAJAR CSV", pd.DataFrame(s.js).to_csv(index=False).encode('utf-8'), "partido.csv")
st.markdown("<p style='text-align:center;color:gray;'>Desarrollado por Kike v1.2</p>", 1)
