import streamlit as st
import pandas as pd
import time
import io
from streamlit_autorefresh import st_autorefresh
st.set_page_config(page_title="LUD v3.5 iPad Fix", layout="wide")
s = st.session_state
if 'js' not in s:
    n = ["Serra","Julian","Omar","Tony","Rochina","Benages","Pedrito","Parre Jr","Baeza","Manu","Pedro Toro","Paco Silla","Jose","Coque","Nacho Gomez"]
    s.js = [{"n":x,"t":0.0,"t1":0.0,"i":None,"p":False,"g":0,"s":0,"e":0,"r":0} for x in n]
    s.ml,s.mr,s.fl,s.fr,s.ta,s.ic,s.on,s.pa,s.q1,s.q2,s.ex = 0,0,0,0,0.0,None,False,"1T",None,None,False
if not s.ex: st_autorefresh(1000, key="f5")
ah = time.time()
tr = s.ta + (ah - s.ic if s.on and s.ic else 0)
rem = max(0, 1200 - tr)
c1,c2,c3 = st.columns([3,2,1])
with c1:
    ci,ct = st.columns([0.6,3.4])
    ci.image("https://upload.wikimedia.org/wikipedia/en/thumb/7/7b/Levante_Uni%C3%B3n_Deportiva%2C_S.A.D._logo.svg/200px-Levante_Uni%C3%B3n_Deportiva%2C_S.A.D._logo.svg.png", width=50)
    rv = ct.text_input("R", "RIVAL", label_visibility="collapsed").upper()
with c2:
    qa = s.q1 if s.pa == "1T" else s.q2
    if qa is None:
        sel = st.multiselect(f"Q {s.pa}", [j["n"] for j in s.js], max_selections=5)
        if st.button("🔒 FIJAR"):
            if len(sel)==5:
                if s.pa=="1T": s.q1=sel
                else: s.q2=sel
                for j in s.js: j["p"]=(j["n"] in sel); j["i"]=None
                st.rerun()
    else: st.success(f"Q {s.pa}: {','.join(qa)}")
if c3.button("🔄"): s.clear(); st.rerun()
t1,t2,t3 = st.tabs(["⏱️PARTIDO","📊TOTAL","💾FIN"])
with t1:
    m1,m2,m3 = st.columns([2,3,2])
    with m1:
        st.metric("LUD",s.ml,f"F:{s.fl}")
        if st.button("⚽ GOL LUD",use_container_width=1): s.ml+=1; st.rerun()
        f1,f2 = st.columns(2)
        if f1.button("F+",key="flp"): s.fl+=1; st.rerun()
        if f2.button("F-",key="flm"): s.fl=max(0,s.fl-1); st.rerun()
    with m2:
        m,v = divmod(int(rem),60)
        st.markdown(f"<h1 style='text-align:center;font-size:4rem;color:red;margin:0;'>{m:02d}:{v:02d}</h1>",1)
        if not s.on:
            if st.button("▶ START",use_container_width=1,type="primary"):
                s.ic,s.on = ah,True
                for j in s.js: 
                    if j["p"]: j["i"]=ah
                st.rerun()
        else:
            if st.button("⏸ STOP",use_container_width=1):
                s.ta += ah-s.ic
                s.on,s.ic = False,None
                for j in s.js:
                    if j["p"] and j["i"]: j["t"]+=ah-j["i"]; j["i"]=None
                st.rerun()
    with m3:
        st.metric(rv[:5],s.mr,f"F:{s.fr}")
        if st.button(f"⚽ GOL {rv[:3]}",use_container_width=1): s.mr+=1; st.rerun()
        r1,r2 = st.columns(2)
        if r1.button("F+",key="frp"): s.fr+=1; st.rerun()
        if r2.button("F-",key="frm"): s.fr=max(0,s.fr-1); st.rerun()
    st.divider()
    cols = st.columns(4)
    for idx,j in enumerate(s.js):
        with cols[idx%4]:
            with st.container(border=True):
                tp = j["t"]+(ah-j["i"] if s.on and j["p"] and j["i"] else 0)
                m,v = divmod(int(tp),60)
                st.write(f"{'🟢' if j['p'] else '🔴'} **{j['n']}** | {m:02d}:{v:02d}")
                # BOTONERA REESTRUCTURADA PARA IPAD (2X2)
                row1_1, row1_2 = st.columns(2)
                if row1_1.button("🎯",key=f"t{idx}",use_container_width=1): j["s"]+=1
                if row1_2.button("🛡️",key=f"r{idx}",use_container_width=1): j["r"]+=1
                row2_1, row2_2 = st.columns(2)
                if row2_1.button("❌",key=f"e{idx}",use_container_width=1): j["e"]+=1
                if row2_2.button("⚽",key=f"g{idx}",use_container_width=1): j["g"]+=1; s.ml+=1; st.rerun()
                st.write("")
                if st.button("CAMBIO",key=f"c{idx}",use_container_width=1):
                    if not j["p"] and sum(1 for x in s.js if x["p"])<5:
                        j["p"],j["i"] = True,(ah if s.on else None)
                    elif j["p"]:
                        if s.on and j["i"]: j["t"]+=ah-j["i"]
                        j["p"],j["i"] = False,None
                    st.rerun()
with t2:
    mc = st.columns(5)
    for idx,j in enumerate(s.js):
        tt = j["t1"]+j["t"]+(ah-j["i"] if s.on and j["p"] and j["i"] else 0)
        m,v = divmod(int(tt),60)
        mc[idx%5].write(f"**{j['n']}**: {m:02d}:{v:02d}")
with t3:
    if s.pa=="1T":
        if st.button("🏁 FIN 1T",use_container_width=1,type="primary"):
            if s.on:
                s.ta+=ah-s.ic
                for j in s.js:
                    if j["p"] and j["i"]: j["t"]+=ah-j["i"]
            for j in s.js: j["t1"]=j["t"]; j["t"]=0.0; j["i"]=None
            s.fl,s.fr,s.ta,s.ic,s.on,s.pa = 0,0,0.0,None,False,"2T"
            st.rerun()
    else: st.success("2T EN CURSO")
    st.divider()
    if st.button("💾 EXCEL FINAL"):
        s.ex = True
        dt = []
        for j in s.js:
            tf = j["t1"]+j["t"]+(ah-j["i"] if s.on and j["p"] and j["i"] else 0)
            m,v = divmod(int(tf),60)
            dt.append({"Jugador":j["n"],"
