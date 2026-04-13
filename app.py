import streamlit as st
import pandas as pd
import time, io
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="LUD Match Control v7.2", layout="wide")

st.markdown("""
    <style>
    .block-container {padding-top:0rem; padding-bottom:0rem; padding-left:0.3rem; padding-right:0.3rem;}
    [data-testid="stVerticalBlock"] > div { gap: 0rem !important; }
    
    /* BOTÓN START/STOP */
    div.stButton > button[key="tm_m"] {
        height: 2.8em !important;
        font-size: 1.1rem !important;
        background-color: #003D7A !important;
        border: 2px solid #ed1c24 !important;
    }

    /* BOTÓN CAMBIO */
    div.stButton > button[key^="c_"] {
        height: 2.4em !important;
        font-size: 0.9rem !important;
        margin-top: 3px !important;
        background-color: #f0f2f6 !important;
        border: 1px solid #ccc !important;
    }

    /* Estilos de botones de Faltas en Footer */
    div.stButton > button[key^="flp"], div.stButton > button[key^="frp"] {
        background-color: #e8f5e9 !important; /* Verde muy suave */
        border: 1px solid #c3e6cb !important;
        color: #155724 !important;
    }
    div.stButton > button[key^="flm"], div.stButton > button[key^="frm"] {
        background-color: #fff5f5 !important; /* Rojo muy suave */
        border: 1px solid #f5c6cb !important;
        color: #721c24 !important;
    }

    /* Botón Reset más grande y visible */
    div.stButton > button[key="main_reset_btn"] {
        font-size: 1.2rem !important;
        height: 2.2em !important;
        background-color: #fff1f1 !important;
        border: 1px solid #ffcccc !important;
    }

    @keyframes blink { 0% {opacity: 1;} 50% {opacity: 0.3;} 100% {opacity: 1;} }
    .blink { animation: blink 1s infinite; }
    .bonus-faltas { color: #ff0000; font-weight: 900; animation: blink 0.8s infinite; }
    .tm-alert { color: #ff9800; font-weight: bold; animation: blink 0.5s infinite; }
    
    /* General botones footer */
    div.stButton > button { border-radius: 4px; height: 2em; width: 100%; font-size: 0.8rem !important; font-weight: bold !important; padding: 0px !important; }
    div.stButton > button:active { transform: scale(0.95); background-color: #003D7A !important; color: white !important; }
    
    .header-container { display: flex; align-items: center; justify-content: center; gap: 5px; border-bottom: 2px solid #ed1c24; margin-bottom: 2px; }
    .title {color:#003D7A; font-size:1rem; font-weight:bold; margin:0;}
    .label-x {font-size:0.6rem; font-weight:700; text-align:center; color:#444; text-transform: uppercase; margin-bottom: 2px;}
    .mini-stats { font-size: 0.9rem !important; font-weight: 900 !important; color: #111; line-height: 1.1; margin-top: 2px; }
    .footer-control { background-color: #f1f3f6; padding: 10px; border-radius: 10px; border: 1px solid #ccd1d9; margin-top: 8px; }
    </style>
    """, unsafe_allow_html=True)

if 'js' not in st.session_state:
    n = ["Serra","Julian","Omar","Tony","Rochina","Benages","Pedrito","Parre Jr","Baeza","Manu","Pedro Toro","Paco Silla","Jose","Coque","Nacho Gomez"]
    st.session_state.js = [{"n":x,"tt":0.0,"tot":0.0,"r":0,"i":None,"p":False,"g":0} for x in n]
    st.session_state.gi, st.session_state.pm, st.session_state.pp, st.session_state.dok, st.session_state.dko = [],0,0,0,0
    st.session_state.al, st.session_state.rl, st.session_state.ar, st.session_state.rr, st.session_state.ml, st.session_state.mr, st.session_state.fl, st.session_state.fr = 0,0,0,0,0,0,0,0
    st.session_state.ta, st.session_state.ic, st.session_state.on, st.session_state.pa, st.session_state.ex = 0.0,None,False,"1T",False
    st.session_state.rv, st.session_state.fe = "RIVAL", datetime.now().strftime("%d/%m/%Y")
    st.session_state.tm, st.session_state.tm_i = False, None

s = st.session_state
if not s.ex: st_autorefresh(1000, key="f5_v72")

ah = time.time()
tr = s.ta + (ah - s.ic if s.on and s.ic else 0)
rem = max(0, 1200 - tr)
min_game = int((tr if s.pa=="1T" else tr+1200) // 60)

tm_sec = 0
if s.tm:
    elapsed = ah - s.tm_i
    tm_sec = max(0, 60 - int(elapsed))
    if tm_sec == 0: s.tm = False

# CABECERA
st.markdown(f'<div class="header-container"><img src="https://upload.wikimedia.org/wikipedia/en/thumb/7/7b/Levante_Uni%C3%B3n_Deportiva%2C_S.A.D._logo.svg/200px-Levante_Uni%C3%B3n_Deportiva%2C_S.A.D._logo.svg.png" width="25"><h1 class="title">LUD MATCH CONTROL</h1></div>', unsafe_allow_html=True)

# FILA DE CONFIGURACIÓN REORGANIZADA (Reset grande arriba)
d1, d2, d3, d4 = st.columns([1.5, 1, 1, 0.5])
s.rv = d1.text_input("RIVAL", s.rv, key="irv", label_visibility="collapsed").upper()
s.fe = d2.text_input("FECHA", s.fe, key="ife", label_visibility="collapsed")
with d3:
    with st.popover("5 INICIAL", use_container_width=True):
        cp = sum(1 for x in s.js if x["p"])
        for j in s.js:
            if st.button(f"{'✅' if j['p'] else '⬜'} {j['n']}", key=f"in_{j['n']}", use_container_width=True):
                if j["p"]: j["p"], j["i"], j["r"] = False, None, 0
                elif cp < 5: j["p"], j["r"] = True, 1; j["i"] = ah if s.on else None
                st.rerun()
# Botón Reset más grande y en su sitio
if d4.button("🗑️", key="main_reset_btn", use_container_width=True): st.session_state.clear(); st.rerun()

# MARCADOR
c1, c2, c3 = st.columns([2, 4, 2])
with c1:
    st.metric(f"LUD", s.ml)
    if st.button("⚽ GOL LUD", key="btn_gol_lud_direct"):
        s.ml += 1
        s.gi.append({"team":"LUD", "name":"LUD", "m":min_game})
        st.rerun()

with c2:
    if s.tm:
        st.markdown(f"<h1 style='text-align:center;font-size:2.2rem;color:orange;margin:0;' class='tm-alert'>TM {tm_sec}s</h1>",1)
    else:
        mr_v, sr_v = divmod(int(rem), 60)
        st.markdown(f"<h1 style='text-align:center;font-size:2.8rem;color:red;margin:0;line-height:1;'>{mr_v:02d}:{sr_v:02d}</h1>",1)
    if st.button("▶ START / STOP ⏸", key="tm_m", type="primary", use_container_width=True):
        if not s.on:
            s.ic, s.on, s.tm = ah, True, False
            for j in s.js: 
                if j["p"]: j["i"]=ah
        else:
            s.ta += ah-s.ic; s.on, s.ic = False, None
            for j in s.js:
                if j["p"] and j["i"]: d_d = ah-j["i"]; j["tot"]+=d_d; j["tt"]+=d_d; j["i"]=None
        st.rerun()

with c3:
    st.metric(s.rv[:8], s.mr)
    if st.button(f"⚽ GOL {s.rv[:8]}", key="gr_r_dynamic"):
        s.mr+=1
        s.gi.append({"team":"RIVAL", "name":s.rv[:8], "m":min_game})
        st.rerun()

# LINEA DE TIEMPO
tl_html = '<div style="display:flex; flex-wrap:wrap; gap:2px; justify-content:center; background:#eee; border-radius:4px; padding:2px; margin:4px 0;">'
for g in s.gi:
    est = "background:#003D7A;color:white;" if g["team"]=="LUD" else "background:white;color:black;border:1px solid #ccc;"
    label = g["name"][:3]
    tl_html += f'<span style="font-size:0.6rem; font-weight:bold; padding:1px 3px; border-radius:2px; {est}">{g["m"]}\'{label}</span>'
st.markdown(tl_html + '</div>', 1)

# JUGADORES
cols = st.columns(5)
for idx, j in enumerate(s.js):
    with cols[idx%5]:
        with st.container(border=True):
            tc = j["tt"] + (ah-j["i"] if s.on and j["p"] and j["i"] else 0)
            mj, vj = divmod(int(tc), 60)
            tl = j["tot"] + (ah-j["i"] if s.on and j["p"] and j["i"] else 0)
            mt, vt = divmod(int(tl), 60)
            fat = "<span class='blink tm-alert'>⚠️</span>" if mj >= 5 else ""
            st.markdown(f"<p style='margin:0;font-size:0.7rem;'>{'🟢' if j['p'] else '🔴'} <b>{j['n']}</b> <span style='float:right; font-weight:900;'>R:{j['r']}</span></p>", 1)
            st.markdown(f"<h4 style='margin:0;text-align:center;font-size:1.1rem;'>{mj:02d}:{vj:02d} {fat}</h4>", 1)
            st.markdown(f"<div class='mini-stats' style='display:flex;justify-content:space-between;'><span>⚽ {j['g']}</span><span>Σ {mt:02d}:{vt:02d}</span></div>", 1)
            if st.button("CAMBIO", key=f"c_{idx}", use_container_width=True):
                if not j["p"] and sum(1 for x in s.js if x["p"])<5:
                    j["p"], j["i"], j["r"] = True, (ah if s.on else None), j["r"]+1
                    j["tt"] = 0.0
                elif j["p"]:
                    if s.on and j["i"]: d_d = ah-j["i"]; j["tot"]+=d_d; j["tt"]+=d_d
                    j["p"], j["i"] = False, None
                st.rerun()

# FOOTER REDISEÑADO (Botones grandes)
st.markdown("<div class='footer-control'>", unsafe_allow_html=True)
b1, b2, b3 = st.columns([3.5, 3, 3.5])

with b1: # CONTROL LUD REFORZADO
    st.markdown(f"<div class='label-x'>FALTAS LUD: <span class='{'bonus-faltas' if s.fl>=5 else ''}'>{s.fl}</span></div>", 1)
    c_f, c_tm = st.columns([2, 1])
    with c_f:
        if st.button("FALTA +", key="flp_big"): s.fl+=1; st.rerun()
        if st.button("FALTA -", key="flm_big"): s.fl=max(0, s.fl-1); st.rerun()
    with c_tm:
        if st.button("TM", key="tm_l_btn", h=True): # h=True para forzar altura completa si el CSS falla
            if s.on: s.ta += ah-s.ic; s.on, s.ic = False, None
            s.tm, s.tm_i = True, ah; st.rerun()
    c_t = st.columns(2)
    if c_t[0].button(f"🟨 {s.al}", key="tal_l"): s.al+=1; st.rerun()
    if c_t[1].button(f"🟥 {s.rl}", key="trl_l"): s.rl+=1; st.rerun()

with b2: # PORTERO Y DUELOS (Igual de anchos)
    st.markdown("<div class='label-x'>TÉCNICO LUD</div>", 1)
    c_p, c_d = st.columns(2)
    with c_p:
        if st.button(f"🧤 {s.pm}", key="pm_b"): s.pm+=1; st.rerun()
        if st.button(f"👟 {s.pp}", key="pp_b"): s.pp+=1; st.rerun()
    with c_d:
        td_v = s.dok + s.dko
        if st.button(f"✅ D: {(s.dok/td_v*100 if td_v>0 else 0):.0f}%", key="dok_b"): s.dok+=1; st.rerun()
        if st.button(f"❌ D: {s.dko}", key="dko_b"): s.dko+=1; st.rerun()

with b3: # CONTROL RIVAL REFORZADO
    st.markdown(f"<div class='label-x'>FALTAS {s.rv[:8]}: <span class='{'bonus-faltas' if s.fr>=5 else ''}'>{s.fr}</span></div>", 1)
    c_tmr, c_fr = st.columns([1, 2])
    with c_tmr:
        if st.button("TM", key="tm_r_btn"):
            if s.on: s.ta += ah-s.ic; s.on, s.ic = False, None
            s.tm, s.tm_i = True, ah; st.rerun()
    with c_fr:
        if st.button("FALTA +", key="frp_big"): s.fr+=1; st.rerun()
        if st.button("FALTA -", key="frm_big"): s.fr=max(0, s.fr-1); st.rerun()
    c_tr = st.columns(2)
    if c_tr[0].button(f"🟨 {s.ar}", key="tar_r"): s.ar+=1; st.rerun()
    if c_tr[1].button(f"🟥 {s.rr}", key="trr_r"): s.rr+=1; st.rerun()
st.markdown("</div>", unsafe_allow_html=True)
