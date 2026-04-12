import streamlit as st
import pandas as pd
import time
import io
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="LUD v4.6 Fichas Pro", layout="wide")

st.markdown("""
    <style>
    .block-container {padding-top: 1rem; padding-bottom: 0rem;}
    /* Compactar la ficha del jugador */
    [data-testid="stVerticalBlock"] > div { gap: 0rem; }
    
    /* Diseño de botones integrados (cuadrados) */
    div.stButton > button {
        border-radius: 0px; /* Cuadrados */
        height: 2.2em;
        font-size: 0.9rem !important;
        margin: 0px !important;
        border: 0.5px solid #e0e0e0 !important;
        background-color: #f8f9fa;
    }
    
    /* Color especial al pulsar */
    div.stButton > button:active {
        background-color: #003D7A !important;
        color: white !important;
    }

    .goleador-box { background-color: #f0f2f6; padding: 5px; border-radius: 5px; font-size: 0.8rem; margin-bottom: 2px; border-left: 3px solid #003D7A; }
    .label-mini { font-size: 0.7rem; font-weight: bold; text-align: center; margin-top: 5px; color: #666; }
    </style>
    """, unsafe_allow_html=True)

def init_state(force=False):
    if 'js' not in st.session_state or force:
        n = ["Serra","Julian","Omar","Tony","Rochina","Benages","Pedrito","Parre Jr","Baeza","Manu","Pedro Toro","Paco Silla","Jose","Coque","Nacho Gomez"]
        st.session_state.js = [{"n":x,"t_turno":0.0,"t_total":0.0,"rot":0,"i":None,"p":False,"g":0,"s":0,"e":0,"r":0} for x in n]
        st.session_state.goles_info = []
        st.session_state.p_mano, st.session_state.p_pie = 0, 0
        st.session_state.ta_l, st.session_state.tr_l, st.session_state.ta_r, st.session_state.tr_r = 0, 0, 0, 0
        st.session_state.ml, st.session_state.mr, st.session_state.fl, st.session_state.fr = 0, 0, 0, 0
        st.session_state.ta, st.session_state.ic, st.session_state.on, st.session_state.pa = 0.0, None, False, "1T"
        st.session_state.ex = False

init_state()
s = st.session_state
if not s.ex: st_autorefresh(1000, key="f5_refresh_v46")

ah = time.time()
tr = s.ta + (ah - s.ic if s.on and s.ic else 0)
rem = max(0, 1200 - tr)
min_p, seg_p = divmod(int(tr if s.pa=="1T" else tr+1200), 60)

# --- MARCADOR SUPERIOR ---
c1,c2,c3 = st.columns([2,3,2])
with c1:
    st.metric(f"LUD | ⚽ {s.ml} | ❌ {s.fl}", s.ml)
    f1,f2 = st.columns(2)
    f1.button("F+", key="k_flp") and exec("s.fl+=1; st.rerun()")
    f2.button("F-", key="k_flm") and exec("s.fl=max(0,s.fl-1); st.rerun()")
    tjl, tcl = st.columns(2)
    tjl.button(f"🟨 {s.ta_l}", key="k_tal") and exec("s.ta_l+=1; st.rerun()")
    tcl.button(f"🟥 {s.tr_l}", key="k_trl") and exec("s.tr_l+=1; st.rerun()")
    st.markdown("<div class='label-mini'>🧤 PORTERO</div>", 1)
    pm, pp = st.columns(2); pm.button(f"🧤 {s.p_mano}", key="k_pm") and exec("s.p_mano+=1; st.rerun()"); pp.button(f"👟 {s.p_pie}", key="k_pp") and exec("s.p_pie+=1; st.rerun()")

with c2:
    m,v = divmod(int(rem),60)
    st.markdown(f"<h1 style='text-align:center;font-size:3.5rem;color:red;margin:0;'>{m:02d}:{v:02d}</h1>",1)
    if st.button("▶ START / ⏸ STOP", use_container_width=1, key="k_timer"):
        if not s.on:
            s.ic, s.on = ah, True
            for j in s.js: 
                if j["p"]: j["i"]=ah
        else:
            s.ta += ah-s.ic; s.on, s.ic = False, None
            for j in s.js:
                if j["p"] and j["i"]: dur = ah-j["i"]; j["t_turno"]+=dur; j["t_total"]+=dur; j["i"]=None
        st.rerun()
    with st.expander("⚽ GOLES", expanded=True):
        for g in s.goles_info[-2:]: st.markdown(f"<div class='goleador-box'><b>{g['min']}:{g['seg']}</b> - {g['jugador']}</div>", 1)

with c3:
    st.button("🗑️ RESET", key="k_reset", use_container_width=1) and exec("init_state(True); st.rerun()")
    st.metric(f"RIVAL | ⚽ {s.mr} | ❌ {s.fr}", s.mr)
    r1,r2 = st.columns(2)
    r1.button("F+", key="k_frp") and exec("s.fr+=1; st.rerun()")
    r2.button("F-", key="k_frm") and exec("s.fr=max(0,s.fr-1); st.rerun()")
    tjr, tcr = st.columns(2)
    tjr.button(f"🟨 {s.ta_r}", key="k_tar") and exec("s.ta_r+=1; st.rerun()")
    tcr.button(f"🟥 {s.tr_r}", key="k_trr") and exec("s.tr_r+=1; st.rerun()")
    st.button("⚽ GOL RIVAL", use_container_width=1, key="k_g_riv") and exec("s.mr+=1; s.goles_info.append({'jugador':'RIVAL','min':f'{min_p:02d}','seg':f'{seg_p:02d}'}); st.rerun()")

st.divider()

# --- JUGADORES (Diseño de cuadrados integrados) ---
cols = st.columns(5)
for idx, j in enumerate(s.js):
    with cols[idx%5]:
        with st.container(border=True):
            t_d = j["t_turno"] + (ah - j["i"] if s.on and j["p"] and j["i"] else 0)
            mj,vj = divmod(int(t_d), 60)
            st.markdown(f"<p style='margin:0;font-size:0.7rem;'>{'🟢' if j['p'] else '🔴'} <b>{j['n']}</b> (R:{j['rot']})</p>", 1)
            st.markdown(f"<p style='margin:0;font-size:0.85rem;text-align:right;'><b>{mj:02d}:{vj:02d}</b></p>", 1)
            
            # Botonera integrada (Cuadros pegados)
            b1, b2, b3, b4 = st.columns([1,1,1,1], gap="small")
            b1.button("🎯", key=f"t{idx}") and exec("j['s']+=1")
            b2.button("🛡️", key=f"r{idx}") and exec("j['r']+=1")
            b3.button("❌", key=f"e{idx}") and exec("j['e']+=1")
            if b4.button("⚽", key=f"g{idx}"):
                j["g"]+=1; s.ml+=1
                s.goles_info.append({"jugador":j["n"],"min":f"{min_p:02d}","seg":f"{seg_p:02d}"})
                st.rerun()
            
            if st.button("CAMBIO", key=f"c{idx}", use_container_width=1):
                if not j["p"] and sum(1 for x in s.js if x["p"])<5:
                    j["p"], j["i"], j["rot"] = True, (ah if s.on else None), j["rot"]+1
                    j["t_turno"] = 0.0
                elif j["p"]:
                    if s.on and j["i"]: dur = ah - j["i"]; j["t_total"]+=dur; j["t_turno"]+=dur
                    j["p"], j["i"] = False, None
                st.rerun()

t_acc, t_fin = st.tabs(["📊 TOTALES", "💾 EXCEL"])
with t_acc:
    st.write(f"Portería: 🧤 {s.p_mano} | 👟 {s.p_pie}")
    mc = st.columns(5)
    for idx, j in enumerate(s.js):
        t_tot = j["t_total"] + (ah - j["i"] if s.on and j["p"] and j["i"] else 0)
        m,v = divmod(int(t_tot),60)
        mc[idx%5].write(f"**{j['n']}**: {m:02d}:{v:02d}")

with t_fin:
    if s.pa=="1T" and st.button("🏁 FIN 1T", use_container_width=1):
        if s.on: s.ta += ah-s.ic
        for j in s.js:
            if j["p"] and j["i"]: dur = ah-j["i"]; j["t_total"]+=dur; j["t_turno"]+=dur
            j["t_turno"], j["i"] = 0.0, None
        s.fl, s.fr, s.ta, s.ic, s.on, s.pa = 0, 0, 0.0, None, False, "2T"
        st.rerun()
    st.divider()
    if st.button("📊 GENERAR EXCEL"):
        dt = [{"Jugador":j["n"],"Min":f"{divmod(int(j['t_total']),60)[0]:02d}:{divmod(int(j['t_total']),60)[1]:02d}","G":j["g"],"R":j["rot"]} for j in s.js]
        out = io.BytesIO()
        with pd.ExcelWriter(out, engine='xlsxwriter') as w: pd.DataFrame(dt).to_excel(w, index=False)
        st.download_button("📥 DESCARGAR", out.getvalue(), "LUD_Report.xlsx")
