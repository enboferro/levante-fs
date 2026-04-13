import streamlit as st
import pandas as pd
import time, io
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="LUD Match Control v6.5", layout="wide")

# CSS: ANIMACIONES DE ALERTA Y COMPACTACIÓN EXTREMA
st.markdown("""
    <style>
    .block-container {padding-top:0rem; padding-bottom:0rem; padding-left:0.3rem; padding-right:0.3rem;}
    [data-testid="stVerticalBlock"] > div { gap: 0rem !important; }
    [data-testid="column"] { padding: 0px 1px !important; }
    
    @keyframes blink { 0% {opacity: 1;} 50% {opacity: 0.3;} 100% {opacity: 1;} }
    .blink { animation: blink 1s infinite; }
    .bonus-faltas { color: #ff0000; font-weight: 900; animation: blink 0.8s infinite; }
    .tm-alert { color: #ff9800; font-weight: bold; animation: blink 0.5s infinite; }
    
    div.stButton > button { border-radius: 4px; height: 1.8em; width: 100%; font-size: 0.75rem !important; font-weight: bold !important; padding: 0px !important; }
    .header-container { display: flex; align-items: center; justify-content: center; gap: 5px; border-bottom: 2px solid #ed1c24; margin-bottom: 2px; }
    .title {color:#003D7A; font-size:1.1rem; font-weight:bold; margin:0;}
    .label-x {font-size:0.55rem; font-weight:700; text-align:center; color:#444; text-transform: uppercase;}
    .mini-stats { font-size: 0.7rem; font-weight: 700; color: #333; line-height: 1.0; margin-top: 2px; }
    
    /* Ajuste de contenedor de fichas */
    [data-testid="stVerticalBlockBorderWrapper"] { padding: 2px !important; }
    hr { margin: 0.2rem 0px !important; }
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
if not s.ex: st_autorefresh(1000, key="f5_v65")

ah = time.time()
tr = s.ta + (ah - s.ic if s.on and s.ic else 0)
rem = max(0, 1200 - tr)
min_game = int((tr if s.pa=="1T" else tr+1200) // 60)

# LÓGICA CUENTA REGRESIVA TIEMPO MUERTO (60s)
tm_sec = 0
if s.tm:
    elapsed = ah - s.tm_i
    tm_sec = max(0, 60 - int(elapsed))
    if tm_sec == 0: s.tm = False

st.markdown(f'<div class="header-container"><img src="https://upload.wikimedia.org/wikipedia/en/thumb/7/7b/Levante_Uni%C3%B3n_Deportiva%2C_S.A.D._logo.svg/200px-Levante_Uni%C3%B3n_Deportiva%2C_S.A.D._logo.svg.png" width="25"><h1 class="title">LUD MATCH CONTROL</h1></div>', unsafe_allow_html=True)

d1, d2, d3, d4 = st.columns([1.5, 1, 1, 0.5])
s.rv = d1.text_input("RIVAL", s.rv, key="irv", label_visibility="collapsed").upper()
s.fe = d2.text_input("FECHA", s.fe, key="ife", label_visibility="collapsed")
with d3:
    with st.popover("5 INICIAL", use_container_width=True):
        cant_p = sum(1 for x in s.js if x["p"])
        for j in s.js:
            if st.button(f"{'✅' if j['p'] else '⬜'} {j['n']}", key=f"in_{j['n']}", use_container_width=True):
                if j["p"]: j["p"], j["i"], j["r"] = False, None, 0
                elif cant_p < 5: j["p"], j["r"] = True, 1; j["i"] = ah if s.on else None
                st.rerun()
if d4.button("🗑️"): st.session_state.clear(); st.rerun()

c1, c2, c3 = st.columns([3.1, 2.6, 3.1])

with c1:
    f_st = "class='bonus-faltas'" if s.fl >= 5 else ""
    st.markdown(f"<h3 style='margin:0; font-size:0.95rem;'>LUD | ⚽ {s.ml} | <span {f_st}>❌ {s.fl}</span></h3>", 1)
    cg, cf, ctm = st.columns([1.2, 0.9, 0.8])
    with cg:
        with st.popover("⚽ GOL", use_container_width=True):
            for i,j in enumerate(s.js):
                if st.button(j["n"], key=f"g_l_{i}"):
                    s.ml+=1; j["g"]+=1; s.gi.append({"team":"LUD", "j":j["n"], "m":min_game}); st.rerun()
    if cf.button("F+", key="flp"): s.fl+=1; st.rerun()
    if ctm.button("TM", key="tm_l"):
        if s.on: s.ta += ah-s.ic; s.on, s.ic = False, None
        s.tm, s.tm_i = True, ah; st.rerun()
    
    tc, pc, dc = st.columns([1, 1.2, 1.2])
    with tc:
        if st.button(f"🟨{s.al}"): s.al+=1; st.rerun()
        if st.button(f"🟥{s.rl}"): s.rl+=1; st.rerun()
    with pc:
        st.markdown("<div class='label-x'>PORTERO</div>", 1)
        px1, px2 = st.columns(2)
        if px1.button(f"🧤{s.pm}"): s.pm += 1; st.rerun()
        if px2.button(f"👟{s.pp}"): s.pp += 1; st.rerun()
    with dc:
        tot_d = s.dok + s.dko
        st.markdown(f"<div class='label-x'>⚔️ <span class='perc-bold'>{(s.dok/tot_d*100 if tot_d>0 else 0):.0f}%</span></div>", 1)
        dx1, dx2 = st.columns(2)
        if dx1.button(f"✅{s.dok}"): s.dok += 1; st.rerun()
        if dx2.button(f"❌{s.dko}"): s.dko += 1; st.rerun()

with c2:
    if s.tm:
        estilo_tm = "class='tm-alert'" if tm_sec <= 10 else ""
        st.markdown(f"<h1 style='text-align:center;font-size:2.8rem;color:orange;margin:0;' {estilo_tm}>TM {tm_sec}s</h1>",1)
    else:
        mr_v, sr_v = divmod(int(rem), 60)
        st.markdown(f"<h1 style='text-align:center;font-size:3rem;color:red;margin:0;line-height:1;'>{mr_v:02d}:{sr_v:02d}</h1>",1)
    
    if st.button("▶ START/STOP", type="primary"):
        if not s.on:
            s.ic, s.on, s.tm = ah, True, False
            for j in s.js: 
                if j["p"]: j["i"]=ah
        else:
            s.ta += ah-s.ic; s.on, s.ic = False, None
            for j in s.js:
                if j["p"] and j["i"]: d_d = ah-j["i"]; j["tot"]+=d_d; j["tt"]+=d_d; j["i"]=None
        st.rerun()
    
    tl_html = '<div style="display:flex; flex-wrap:wrap; gap:2px; justify-content:center; background:#eee; border-radius:4px; padding:1px;">'
    for g in s.gi:
        est = "background:#003D7A;color:white;" if g["team"]=="LUD" else "background:white;color:black;border:1px solid #ccc;"
        tl_html += f'<span style="font-size:0.6rem; font-weight:bold; padding:1px 3px; border-radius:2px; {est}">{g["m"]}\'{g["j"][:3]}</span>'
    st.markdown(tl_html + '</div>', 1)

with c3:
    f_st_r = "class='bonus-faltas'" if s.fr >= 5 else ""
    st.markdown(f"<h3 style='margin:0; font-size:0.95rem; text-align:right;'>{s.rv[:8]} | ⚽ {s.mr} | <span {f_st_r}>❌ {s.fr}</span></h3>", 1)
    ctm_r, cf_r, cg_r = st.columns([0.8, 0.9, 1.2])
    if ctm_r.button("TM", key="tm_r"):
        if s.on: s.ta += ah-s.ic; s.on, s.ic = False, None
        s.tm, s.tm_i = True, ah; st.rerun()
    if cf_r.button("F+", key="frp"): s.fr+=1; st.rerun()
    if cg_r.button("⚽ GOL", key="gr_r"): s.mr+=1; s.gi.append({"team":"RIVAL", "j":"RIV", "m":min_game}); st.rerun()
    tr1, tr2 = st.columns(2)
    if tr1.button(f"🟨{s.ar}", key="tar_r"): s.ar+=1; st.rerun()
    if tr2.button(f"🟥{s.rr}", key="trr_r"): s.rr+=1; st.rerun()

st.divider()

cols = st.columns(5)
for idx, j in enumerate(s.js):
    with cols[idx%5]:
        with st.container(border=True):
            tc = j["tt"] + (ah-j["i"] if s.on and j["p"] and j["i"] else 0)
            mj, vj = divmod(int(tc), 60)
            tl = j["tot"] + (ah-j["i"] if s.on and j["p"] and j["i"] else 0)
            mt, vt = divmod(int(tl), 60)
            fat = "<span class='blink tm-alert'>⚠️</span>" if mj >= 5 else ""
            st.markdown(f"<p style='margin:0;font-size:0.7rem;'>{'🟢' if j['p'] else '🔴'} <b>{j['n']}</b> <span style='float:right; font-weight:800;'>R:{j['r']}</span></p>", 1)
            st.markdown(f"<h4 style='margin:0;text-align:center;font-size:1.1rem;'>{mj:02d}:{vj:02d} {fat}</h4>", 1)
            st.markdown(f"<div class='mini-stats' style='display:flex;justify-content:space-between;'><span>⚽ <b>{j['g']}</b></span><span>Σ <b>{mt:02d}:{vt:02d}</b></span></div>", 1)
            if st.button("CAMBIO", key=f"c_{idx}"):
                if not j["p"] and sum(1 for x in s.js if x["p"])<5:
                    j["p"], j["i"], j["r"] = True, (ah if s.on else None), j["r"]+1
                    j["tt"] = 0.0
                elif j["p"]:
                    if s.on and j["i"]: d_d = ah-j["i"]; j["tot"]+=d_d; j["tt"]+=d_d
                    j["p"], j["i"] = False, None
                st.rerun()
