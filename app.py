import streamlit as st
import pandas as pd
import time
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="LUD FS", layout="wide")
st_autorefresh(interval=1000, key="f5")
ss = st.session_state

# 1. INICIALIZACIÓN (Solo lo esencial)
if 'js' not in ss:
    ss.js = [{"id":i,"n":f"Jugador {i+1}","t1":0.0,"t2":0.0,"ini":None,"p":False,"g":0,"t":0,"per":0,"rec":0} for i in range(14)]
if 'rt1' not in ss:
    ss.rt1, ss.rt2, ss.pt, ss.ml, ss.mr, ss.fl, ss.fr = 0.0, 0.0, "T1", 0, 0, 0, 0
if 'ac' not in ss:
    ss.ac, ss.ig = False, None

now = time.time()

# 2. CABECERA
st.title("⚽ LEVANTE UD FS - PANEL")
col_r, col_f, col_res = st.columns([2,2,1])
riv = col_r.text_input("RIVAL", "RIVAL").upper()
fec = col_f.date_input("FECHA", datetime.now())
if col_res.button("RESET TOTAL"):
    ss.clear()
    st.rerun()

# 3. MARCADOR Y RELOJ
c1, c2, c3 = st.columns([2, 2, 2])
with c1:
    st.subheader(f"🐸 LUD: {ss.ml}")
    if st.button("⚽ GOL LUD", use_container_width=True): ss.ml += 1; st.rerun()
    if st.button(f"⚠️ FALTAS: {ss.fl}", use_container_width=True, key="fl_l"): ss.fl += 1; st.rerun()

with c2:
    t_v = ss.rt1 if ss.pt == "T1" else ss.rt2
    if ss.ac and ss.ig: t_v += now - ss.ig
    m, s = divmod(int(t_v), 60)
    st.markdown(f"<h1 style='text-align:center;'>{m:02d}:{s:02d}</h1>", unsafe_allow_html=True)
    if st.button("▶/⏸ INICIAR-PARAR", use_container_width=True, type="primary"):
        if not ss.ac:
            ss.ac, ss.ig = True, now
            for j in ss.js:
                if j["p"]: j["ini"] = now
        else:
            ss.ac = False
            if ss.pt=="T1": ss.rt1 += now - ss.ig
            else: ss.rt2 += now - ss.ig
            for j in ss.js:
                if j["p"] and j["ini"]:
                    if ss.pt=="T1": j["t1"] += now - j["ini"]
                    else: j["t2"] += now - j["ini"]
                    j["ini"] = None
            ss.ig = None
        st.rerun()

with c3:
    st.subheader(f"🏟️ {riv}: {ss.mr}")
    if st.button(f"⚽ GOL {riv[:3]}", use_container_width=True): ss.mr += 1; st.rerun()
    if st.button(f"⚠️ FALTAS: {ss.fr}", use_container_width=True, key="fl_r"): ss.fr += 1; st.rerun()

# 4. CONTADOR DE PISTA
st.divider()
en_pista = sum(1 for j in ss.js if j["p"])
st.subheader(f"👥 JUGADORES EN PISTA: {en_pista} / 5")

# 5. LISTA DE JUGADORES
for i in range(0, 14, 2):
    cols = st.columns(2)
    for idx, col in enumerate(cols):
        ji = i + idx
        if ji < 14:
            j = ss.js[ji]
            with col:
                with st.container(border=True):
                    c_n, c_t, c_p = st.columns([2, 1, 1])
                    j["n"] = c_n.text_input(f"Nombre {ji}", j["n"], key=f"n{ji}", label_visibility="collapsed")
                    
                    t_j = j["t1"] + j["t2"]
                    if ss.ac and j["p"] and j["ini"]: t_j += now - j["ini"]
                    mj, sj = divmod(int(t_j), 60)
                    c_t.write(f"⏱️ {mj:02d}:{sj:02d}")
                    
                    # Botón Entrar/Salir
                    btn_txt = "🔴 SALIR" if j["p"] else "🟢 ENTRAR"
                    if c_p.button(btn_txt, key=f"bt{ji}"):
                        if not j["p"] and en_pista < 5:
                            j["p"] = True
                            if ss.ac: j["ini"] = now
                        elif j["p"]:
                            if ss.ac and j["ini"]:
                                if ss.pt=="T1": j["t1"] += now - j["ini"]
                                else: j["t2"] += now - j["ini"]
                            j["p"], j["ini"] = False, None
                        st.rerun()
                    
                    # Scouting
                    s1, s2, s3, s4 = st.columns(4)
                    if s1.button(f"🎯{j['t']}", key=f"t{ji}"): j["t"]+=1; st.rerun()
                    if s2.button(f"🛡️{j['rec']}", key=f"r{ji}"): j["rec"]+=1; st.rerun()
                    if s3.button(f"❌{j['per']}", key=f"p{ji}"): j["per"]+=1; st.rerun()
                    if s4.button(f"⚽{j['g']}", key=f"g{ji}"): j["g"]+=1; ss.ml+=1; st.rerun()

# 6. EXPORTAR
st.divider()
if st.button("💾 DESCARGAR RESULTADOS"):
    df = pd.DataFrame([{"Jugador":x["n"],"Goles":x["g"],"Tiros":x["t"],"Robos":x["rec"],"Perdidas":x["per"]} for x in ss.js])
    st.download_button("CONFIRMAR DESCARGA", df.to_csv(index=False).encode('utf-8'), f"LUD_{riv}.csv", "text/csv")
