import streamlit as st
import pandas as pd
import time
import io
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="LUD v4.3 Táctica + Portero", layout="wide")

st.markdown("""
    <style>
    .block-container {padding-top: 1rem; padding-bottom: 0rem;}
    div.stButton > button { border-radius: 5px; height: 2.1em; font-size: 0.85rem !important; }
    .goleador-box { background-color: #f0f2f6; padding: 5px; border-radius: 5px; font-size: 0.8rem; margin-bottom: 2px; border-left: 3px solid #003D7A; }
    .label-mini { font-size: 0.7rem; font-weight: bold; text-align: center; margin-top: 5px; color: #666; }
    </style>
    """, unsafe_allow_html=True)

s = st.session_state
if 'js' not in s:
    n = ["Serra","Julian","Omar","Tony","Rochina","Benages","Pedrito","Parre Jr","Baeza","Manu","Pedro Toro","Paco Silla","Jose","Coque","Nacho Gomez"]
    s.js = [{"n":x,"t_turno":0.0,"t_total":0.0,"rot":0,"i":None,"p":False,"g":0,"s":0,"e":0,"r":0} for x in n]
    s.goles_info = []
    s.p_mano, s.p_pie = 0, 0
    s.ta_l, s.tr_l, s.ta_r, s.tr_r = 0, 0, 0, 0
    s.ml,s.mr,s.fl,s.fr,s.ta,s.ic,s.on,s.pa,s.ex = 0,0,0,0,0.0,None,False,"1T",False

if not s.ex: st_autorefresh(1000, key="f5_refresh_v43")

ah = time.time()
tr = s.ta + (ah - s.ic if s.on and s.ic else 0)
rem = max(0, 1200 - tr)
min_p, seg_p = divmod(int(tr if s.pa=="1T" else tr+1200), 60)

c1,c2,c3 = st.columns([2,3,2])

# COLUMNA IZQUIERDA: LUD + PORTERO
with c1:
    st.metric("LUD",s.ml,f"Faltas: {s.fl}")
    f1,f2 = st.columns(2)
    if f1.button("F+", key="k_flp"): s.fl+=1; st.rerun()
    if f2.button("F-", key="k_flm"): s.fl=max(0,s.fl-1); st.rerun()
    tjl, tcl = st.columns(2)
    if tjl.button(f"🟨 {s.ta_l}", key="k_tal"): s.ta_l+=1; st.rerun()
    if tcl.button(f"🟥 {s.tr_l}", key="k_trl"): s.tr_l+=1; st.rerun()
    
    # --- BLOQUE PORTERO (Debajo de tarjetas LUD) ---
    st.markdown("<div class='label-mini'>🧤 PORTERO</div>", unsafe_allow_html=True)
    pm, pp = st.columns(2)
    if pm.button(f"🧤 {s.p_mano}", key="k_pm", use_container_width=1): s.p_mano += 1; st.rerun()
    if pp.button(f"👟 {s.p_pie}", key="k_pp", use_container_width=1): s.p_pie += 1; st.rerun()
    rm, rp = st.columns(2)
    if rm.button("−", key="k_rm", use_container_width=1): s.p_mano = max(0, s.p_mano-1); st.rerun()
    if rp.button("−", key="k_rp", use_container_width=1): s.p_pie = max(0, s.p_pie-1); st.rerun()

# COLUMNA CENTRAL: CRONO + GOLES
with c2:
    m,v = divmod(int(rem),60)
    st.markdown(f"<h1 style='text-align:center;font-size:3.5rem;color:red;margin:0;'>{m:02d}:{v:02d}</h1>",1)
    if st.button("▶ START / ⏸ STOP", use_container_width=1, key="k_main_timer"):
        if not s.on:
            s.ic, s.on = ah, True
            for j in s.js: 
                if j["p"]: j["i"]=ah
        else:
            s.ta += ah-s.ic
            s.on,s.ic = False,None
            for j in s.js:
                if j["p"] and j["i"]: 
                    dur = ah-j["i"]
                    j["t_turno"] += dur
                    j["t_total"] += dur
                    j["i"]=None
        st.rerun()
    
    with st.expander("⚽ CRONOLOGÍA GOLES", expanded=True):
        if not s.goles_info: st.write("Esperando goles...")
        for g in s.goles_info[-3:]:
            st.markdown(f"<div class='goleador-box'><b>{g['min']}:{g['seg']}</b> - {g['jugador']}</div>", 1)

# COLUMNA DERECHA: RIVAL
with c3:
    st.metric("RIVAL",s.mr,f"Faltas: {s.fr}")
    if st.button("⚽ GOL RIVAL", use_container_width=1, key="k_g_riv"): 
        s.mr+=1
        s.goles_info.append({"jugador":"RIVAL","min":f"{min_p:02d}","seg":f"{seg_p:02d}"})
        st.rerun()
    r1,r2 = st.columns(2)
    if r1.button("F+", key="k_frp"): s.fr+=1; st.rerun()
    if r2.button("F-", key="k_frm"): s.fr=max(0,s.fr-1); st.rerun()
    tjr, tcr = st.columns(2)
    if tjr.button(f"🟨 {s.ta_r}", key="k_tar"): s.ta_r+=1; st.rerun()
    if tcr.button(f"🟥 {s.tr_r}", key="k_trr"): s.tr_r+=1; st.rerun()

st.divider()

# PANEL DE JUGADORES (5 COLUMNAS)
cols = st.columns(5)
for idx,j in enumerate(s.js):
    with cols[idx%5]:
        with st.container(border=True):
            t_d = j["t_turno"] + (ah - j["i"] if s.on and j["p"] and j["i"] else 0)
            mj,vj = divmod(int(t_d), 60)
            st.markdown(f"<p style='margin:0;font-size:0.75rem;'>{'🟢' if j['p'] else '🔴'} <b>{j['n']}</b> <span style='color:gray'>(R:{j['rot']})</span></p>", 1)
            st.markdown(f"<p style='margin:0;font-size:0.85rem;text-align:right;'><b>{mj:02d}:{vj:02d}</b></p>", 1)
            
            b1,b2,b3,b4 = st.columns(4)
            if b1.button("🎯", key=f"k_t_{idx}"): j["s"]+=1
            if b2.button("🛡️", key=f"k_r_{idx}"): j["r"]+=1
            if b3.button("❌", key=f"k_e_{idx}"): j["e"]+=1
            if b4.button("⚽", key=f"k_g_{idx}"): 
                j["g"]+=1; s.ml+=1
                s.goles_info.append({"jugador":j["n"],"min":f"{min_p:02d}","seg":f"{seg_p:02d}"})
                st.rerun()
            
            if st.button("CAMBIO", key=f"k_c_{idx}", use_container_width=1):
                if not j["p"] and sum(1 for x in s.js if x["p"])<5:
                    j["p"], j["i"], j["rot"] = True, (ah if s.on else None), j["rot"]+1
                    j["t_turno"] = 0.0
                elif j["p"]:
                    if s.on and j["i"]: 
                        dur = ah - j["i"]
                        j["t_total"] += dur; j["t_turno"] += dur
                    j["p"], j["i"] = False, None
                st.rerun()

t_acc, t_fin = st.tabs(["📊 ACUMULADOS", "💾 FINALIZAR"])
with t_acc:
    st.write(f"**Paradas Portero:** 🧤 Mano: {s.p_mano} | 👟 Pie: {s.p_pie}")
    mc = st.columns(5)
    for idx,j in enumerate(s.js):
        t_tot = j["t_total"] + (ah - j["i"] if s.on and j["p"] and j["i"] else 0)
        m,v = divmod(int(t_tot),60)
        mc[idx%5].write(f"**{j['n']}**: {m:02d}:{v:02d}")

with t_fin:
    if s.pa=="1T":
        if st.button("🏁 FINALIZAR 1T", key="k_fin1", use_container_width=1):
            if s.on:
                s.ta += ah-s.ic
                for j in s.js:
                    if j["p"] and j["i"]: 
                        dur = ah-j["i"]; j["t_total"]+=dur; j["t_turno"]+=dur
            for j in s.js: j["t_turno"] = 0.0; j["i"] = None
            s.fl, s.fr, s.ta, s.ic, s.on, s.pa = 0, 0, 0.0, None, False, "2T"
            st.rerun()
    st.divider()
    if st.button("📊 GENERAR EXCEL", key="k_gen_ex"):
        s.ex = True
        dt = []
        for j in s.js:
            t_f = j["t_total"] + (ah - j["i"] if s.on and j["p"] and j["i"] else 0)
            m,v = divmod(int(t_f),60)
            dt.append({"Jugador":j["n"],"Minutos":f"{m:02d}:{v:02d}","Goles":j["g"],"Rotaciones":j["rot"],"Tiros":j["s"],"Robos":j["r"],"Perdidas":j["e"]})
        out = io.BytesIO()
        with pd.ExcelWriter(out, engine='xlsxwriter') as w: pd.DataFrame(dt).to_excel(w, index=False)
        st.download_button("📥 DESCARGAR INFORME", out.getvalue(), "LUD_Stats.xlsx", key="k_dl_btn")
        if st.button("VOLVER", key="k_back"): s.ex = False; st.rerun()
