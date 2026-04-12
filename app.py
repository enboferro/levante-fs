import streamlit as st
import pandas as pd
import time, io
from datetime import datetime
from streamlit_autorefresh import st_autorefresh
st.set_page_config(page_title="LUD v5.1", layout="wide")
st.markdown("<style>.block-container{padding-top:0.5rem;} [data-testid='stVerticalBlock']>div{gap:0.1rem;} div.stButton>button{border-radius:5px;height:2em;font-size:0.85rem!important;} .title{text-align:center;color:#003D7A;font-size:1.8rem;font-weight:bold;border-bottom:2px solid #ed1c24;} .g-box{background-color:#f0f2f6;padding:4px;border-radius:5px;font-size:0.8rem;border-left:3px solid #003D7A;}</style>", unsafe_allow_html=True)
if 'js' not in st.session_state:
    n = ["Serra","Julian","Omar","Tony","Rochina","Benages","Pedrito","Parre Jr","Baeza","Manu","Pedro Toro","Paco Silla","Jose","Coque","Nacho Gomez"]
    st.session_state.js = [{"n":x,"tt":0.0,"tot":0.0,"r":0,"i":None,"p":False,"g":0} for x in n]
    st.session_state.gi,st.session_state.pm,st.session_state.pp,st.session_state.dok,st.session_state.dko = [],0,0,0,0
    st.session_state.al,st.session_state.rl,st.session_state.ar,st.session_state.rr,st.session_state.ml,st.session_state.mr,st.session_state.fl,st.session_state.fr = 0,0,0,0,0,0,0,0
    st.session_state.ta,st.session_state.ic,st.session_state.on,st.session_state.pa,st.session_state.ex = 0.0,None,False,"1T",False
    st.session_state.rv,st.session_state.fe = "RIVAL", datetime.now().strftime("%d/%m/%Y")
s = st.session_state
if not s.ex: st_autorefresh(1000, key="f5_v51")
ah = time.time()
tr = s.ta + (ah - s.ic if s.on and s.ic else 0)
rem = max(0, 1200 - tr)
mp, sp = divmod(int(tr if s.pa=="1T" else tr+1200), 60)
st.markdown("<div class='title'>M A T C H &nbsp; C O N T R O L</div>", unsafe_allow_html=True)
d1,d2,d3 = st.columns([2,1,1])
s.rv = d1.text_input("RIVAL", s.rv).upper()
s.fe = d2.text_input("FECHA", s.fe)
if d3.button("🗑️ RESET"): st.session_state.clear(); st.rerun()
st.divider()
c1,c2,c3 = st.columns([2.5,3,2.5])
with c1:
    st.metric(f"LUD | ⚽ {s.ml} | ❌ {s.fl}", s.ml)
    cg,cf1,cf2 = st.columns([2,1,1])
    with cg:
        with st.popover("⚽ GOL", use_container_width=True):
            for j in s.js:
                if st.button(j["n"], key=f"gl_{j['n']}"):
                    s.ml+=1; j["g"]+=1; s.gi.append({"j":j["n"],"m":f"{mp:02d}:{sp:02d}"}); st.rerun()
    if cf1.button("F+", key="flp"): s.fl+=1; st.rerun()
    if cf2.button("F-", key="flm"): s.fl=max(0,s.fl-1); st.rerun()
    t1,t2 = st.columns(2)
    if t1.button(f"🟨 {s.al}"): s.al+=1; st.rerun()
    if t2.button(f"🟥 {s.rl}"): s.rl+=1; st.rerun()
    st.write("🧤 PORTERO")
    p1,p2 = st.columns(2)
    if p1.button(f"🧤 {s.pm}"): s.pm+=1; st.rerun()
    if p2.button(f"👟 {s.pp}"): s.pp+=1; st.rerun()
    st.write("⚔️ DUELOS")
    d_ok,d_ko = st.columns(2)
    if d_ok.button(f"✅ {s.dok}"): s.dok+=1; st.rerun()
    if d_ko.button(f"❌ {s.dko}"): s.dko+=1; st.rerun()
with c2:
    mr, sr = divmod(int(rem), 60)
    st.markdown(f"<h1 style='text-align:center;font-size:3.5rem;color:red;margin:0;'>{mr:02d}:{sr:02d}</h1>",1)
    if st.button("▶ START / ⏸ STOP", use_container_width=1, key="tmr", type="primary"):
        if not s.on:
            s.ic, s.on = ah, True
            for j in s.js: 
                if j["p"]: j["i"]=ah
        else:
            s.ta += ah-s.ic; s.on, s.ic = False, None
            for j in s.js:
                if j["p"] and j["i"]: d=ah-j["i"]; j["tt"]+=d; j["tot"]+=d; j["i"]=None
        st.rerun()
    for g in s.gi[-2:]: st.markdown(f"<div class='g-box'>{g['m']} - {g['j']}</div>", 1)
with c3:
    st.metric(f"{s.rv[:8]} | ⚽ {s.mr} | ❌ {s.fr}", s.mr)
    cg_r,cf1_r,cf2_r = st.columns([2,1,1])
    if cg_r.button("⚽ GOL", key="gr"): s.mr+=1; s.gi.append({"j":s.rv,"m":f"{mp:02d}:{sp:02d}"}); st.rerun()
    if cf1_r.button("F+", key="frp"): s.fr+=1; st.rerun()
    if cf2_r.button("F-", key="frm"): s.fr=max(0,s.fr-1); st.rerun()
    tr1,tr2 = st.columns(2)
    if tr1.button(f"🟨 {s.ar}"): s.ar+=1; st.rerun()
    if tr2.button(f"🟥 {s.rr}"): s.rr+=1; st.rerun()
st.divider()
cols = st.columns(5)
for idx, j in enumerate(s.js):
    with cols[idx%5]:
        with st.container(border=True):
            tc = j["tt"] + (ah-j["i"] if s.on and j["p"] and j["i"] else 0)
            mj, vj = divmod(int(tc), 60)
            st.write(f"{'🟢' if j['p'] else '🔴'} **{j['n']}** (R:{j['r']})")
            st.write(f"**{mj:02d}:{vj:02d}**")
            if st.button("CAMBIO", key=f"c_{idx}", use_container_width=1):
                if not j["p"] and sum(1 for x in s.js if x["p"])<5:
                    j["p"],j["i"],j["r"] = True,(ah if s.on else None),j["r"]+1
                    j["tt"] = 0.0
                elif j["p"]:
                    if s.on and j["i"]: d=ah-j["i"]; j["tot"]+=d; j["tt"]+=d
                    j["p"],j["i"] = False,None
                st.rerun()
t1, t2 = st.tabs(["📊 TOTAL", "💾 EXCEL"])
with t1:
    st.write(f"Duelos: ✅{s.dok} ❌{s.dko} | Port: 🧤{s.pm} 👟{s.pp}")
    mc = st.columns(5)
    for idx, j in enumerate(s.js):
        tl = j["tot"] + (ah-j["i"] if s.on and j["p"] and j["i"] else 0)
        mt, vt = divmod(int(tl), 60)
        mc[idx%5].write(f"{j['n']}: {mt:02d}:{vt:02d}")
with t2:
    if s.pa=="1T" and st.button("🏁 FIN 1T", use_container_width=1):
        if s.on: s.ta += ah-s.ic
        for j in s.js:
            if j["p"] and j["i"]: d=ah-j["i"]; j["tot"]+=d; j["tt"]+=d
            j["tt"],j["i"] = 0.0,None
        s.fl,s.fr,s.ta,s.ic,s.on,s.pa = 0,0,0.0,None,False,"2T"
        st.rerun()
    if st.button("📊 EXCEL"):
        s.ex = True
        dt = [{"Jugador":j["n"],"Min":f"{int(j['tot']//60):02d}:{int(j['tot']%60):02d}","G":j["g"],"R":j["r"]} for j in s.js]
        dt.extend([{"Jugador":"Duelos OK","Min":s.dok},{"Jugador":"Duelos KO","Min":s.dko}])
        out = io.BytesIO()
        with pd.ExcelWriter(out, engine='xlsxwriter') as w: pd.DataFrame(dt).to_excel(w, index=False)
        st.download_button("📥 DESCARGAR", out.getvalue(), f"LUD_{s.rv}.xlsx")
