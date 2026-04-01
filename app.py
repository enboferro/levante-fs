import streamlit as st
import pandas as pd
import time
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="LUD FS PRO", layout="wide", page_icon="🐸")
st_autorefresh(interval=1000, key="futsalrefresh")
ss = st.session_state

st.markdown("""<style>
    .stApp { background-color: #F0F2F6; }
    .header-box { background: linear-gradient(90deg, #003D7A, #7A0019); padding: 15px; border-radius: 15px; color: white; text-align: center; }
    .reloj-box { background-color: #1E1E1E; border: 5px solid #FFD700; border-radius: 30px; padding: 20px; }
    .reloj-text { color: white; font-size: 5rem !important; font-weight: bold; text-align: center; margin: 0; }
    .marcador-card { padding: 20px; border-radius: 20px; color: white; text-align: center; min-height: 200px; }
    .stButton>button { height: 3.5rem; font-weight: bold; border-radius: 10px; }
    .jugador-card { background: white; padding: 10px; border-radius: 12px; border-left: 10px solid #D3D3D3; margin-bottom: 10px; }
</style>""", unsafe_allow_html=True)

if 'js' not in ss:
    ss.js = [{"id":i,"n":f"Jugador {i+1}","t1":0.0,"t2":0.0,"ini":None,"p":False,"e":0,"g":0,"t":0,"per":0,"rec":0} for i in range(14)]
if 'rt1' not in ss: ss.rt1, ss.rt2, ss.pt, ss.ml, ss.mr, ss.fl, ss.fr = 0.0, 0.0, "T1", 0, 0, 0, 0
if 'ac' not in ss: ss.ac, ss.ig, ss.pos_activa = False, None, "NEUTRAL"
if 't_pos_lud' not in ss: ss.t_pos_lud, ss.t_pos_riv, ss.t_pos_neu = 0.0, 0.0, 0.0
if 'lpc' not in ss: ss.lpc = time.time()

ahora = time.time()
if ss.ac:
    diff = ahora - ss.lpc
    if ss.pos_activa == "LUD": ss.t_pos_lud += diff
    elif ss.pos_activa == "RIVAL": ss.t_pos_riv += diff
    else: ss.t_pos_neu += diff
ss.lpc = ahora

with st.container():
    c_l, c_i, c_r = st.columns([1, 4, 1])
    c_l.image("https://upload.wikimedia.org/wikipedia/en/thumb/7/7b/Levante_Uni%C3%B3n_Deportiva%2C_S.A.D._logo.svg/1200px-Levante_Uni%C3%B3n_Deportiva%2C_S.A.D._logo.svg.png", width=80)
    with c_i:
        r_col, f_col = st.columns(2)
        riv_n = r_col.text_input("RIVAL", "RIVAL", label_visibility="collapsed").upper()
        f_p = f_col.date_input("FECHA", datetime.now(), label_visibility="collapsed")
        st.markdown(f"<div class='header-box'><h1>LUD vs {riv_n}</h1></div>", unsafe_allow_html=True)
    if c_r.button("⚠️ RESET"): ss.clear(); st.rerun()

col_l, col_c, col_r = st.columns([2, 3, 2])
with col_l:
    c_lud = "#FF0000" if ss.fl >= 5 else "#003D7A"
    st.markdown(f"<div class='marcador-card' style='background:{c_lud}'><h2>LUD</h2><h1 style='font-size:5rem;color:white;'>{ss.ml}</h1><p>FALTAS: {ss.fl}</p></div>", unsafe_allow_html=True)
    cl1, cl2 = st.columns(2)
    if cl1.button("⚽ GOL", key="gl"): ss.ml+=1; st.rerun()
    if cl2.button("⚠️ FALTA", key="fl"): ss.fl+=1; st.rerun()

with col_c:
    t_v = ss.rt1 if ss.pt=="T1" else ss.rt2
    if ss.ac and ss.ig: t_v += ahora - ss.ig
    m, s = divmod(int(t_v), 60)
    st.markdown(f"<div class='reloj-box'><p class='reloj-text'>{m:02d}:{s:02d}</p></div>", unsafe_allow_html=True)
    if not ss.ac:
        if st.button("▶ INICIAR", type="primary", key="st", use_container_width=True):
            ss.ac, ss.ig = True, ahora
            for j in ss.js:
                if j["p"]: j["ini"] = ahora
            st.rerun()
    else:
        if st.button("⏸ PARAR", type="secondary", key="sp", use_container_width=True):
            ss.ac = False
            if ss.pt=="T1": ss.rt1 += ahora - ss.ig
            else: ss.rt2 += ahora - ss.ig
            for j in ss.js:
                if j["p"] and j["ini"]:
                    if ss.pt=="T1": j["t1"] += ahora - j["ini"]
                    else: j["t2"] += ahora - j["ini"]
                    j["ini"] = None
            ss.ig = None; st.rerun()

with col_r:
    c_riv = "#FF0000" if ss.fr >= 5 else "#7A0019"
    st.markdown(f"<div class='marcador-card' style='background:{c_riv}'><h2>{riv_n[:5]}</h2><h1 style='font-size:5rem;color:white;'>{ss.mr}</h1><p>FALTAS: {ss.fr}</p></div>", unsafe_allow_html=True)
    cr1, cr2 = st.columns(2)
    if cr1.button("⚽ GOL ", key="gr"): ss.mr+=1; st.rerun()
    if cr2.button("⚠️ FALTA ", key="fr"): ss.fr+=1; st.rerun()

st.divider()
p1, p2, p3 = st.columns(3)
if p1.button("🔵 LUD", key="pl", use_container_width=True, type="primary" if ss.pos_activa=="LUD" else "secondary"): ss.pos_activa="LUD"; st.rerun()
if p2.button("⚪ NEUTRAL", key="pn", use_container_width=True, type="primary" if ss.pos_activa=="NEUTRAL" else "secondary"): ss.pos_activa="NEUTRAL"; st.rerun()
if p3.button(f"🔴 {riv_n}", key="pr", use_container_width=True, type="primary" if ss.pos_activa=="RIVAL" else "secondary"): ss.pos_activa="RIVAL"; st.rerun()

tp = ss.t_pos_lud + ss.t_pos_riv + 0.001
pl = int((ss.t_pos_lud / tp) * 100)
st.progress(pl/100, text=f"POSESIÓN: LUD {pl}% | {riv_n} {100-pl}%")

st.divider()
for i in range(0, 14, 2):
    cols = st.columns(2)
    for idx, col in enumerate(cols):
        ji = i + idx
        if ji >= 14: break
        j = ss.js[ji]
        with col:
            b_c = "#003D7A" if j["p"] else "#D3D3D3"
            st.markdown(f"<div class='jugador-card' style='border-left-color:{b_c}'>", unsafe_allow_html=True)
            nc, tc, ec = st.columns([2, 1, 1])
            j["n"] = nc.text_input(f"J{ji}", j["n"], key=f"nj{ji}", label_visibility="collapsed")
            tj = j["t1"] + j["t2"]
            if ss.ac and j["p"] and j["ini"]: tj += ahora - j["ini"]
            mj, sj = divmod(int(tj), 60)
            tc.markdown(f"**{mj:02d}:{sj:02d}**")
            if ec.button("🔴" if j["p"] else "🟢", key=f"bt{ji}", use_container_width=True):
                if not j["p"] and sum(1 for x in ss.js if x["p"]) < 5:
                    j["p"], j["e"] = True, j["e"]+1
                    if ss.ac: j["ini"] = ahora
                elif j["p"]:
                    if ss.ac and j["ini"]:
                        if ss.pt=="T1": j["t1"] += ahora - j["ini"]
                        else: j["t2"] += ahora - j["ini"]
                    j["p"], j["ini"] = False, None
                st.rerun()
            s1, s2, s3, s4 = st.columns(4)
            if s1.button(f"🎯{j['t']}", key=f"tj{ji}"): j["t"]+=1; st.rerun()
            if s2.button(f"⚠️{j['per']}", key=f"pj{ji}"): j["per"]+=1; st.rerun()
            if s3.button(f"🛡️{j['rec']}", key=f"rj{ji}"): j["rec"]+=1; st.rerun()
            if s4.button(f"⚽{j['g']}", key=f"gj{ji}"): j["g"]+=1; ss.ml+=1; st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

st.divider()
if st.button("💾 DESCARGAR CSV", key="dld", use_container_width=True):
    df = pd.DataFrame([{"Jugador":x["n"],"Min":round((x
