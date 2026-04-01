import streamlit as st
import pandas as pd
import time

st.set_page_config(page_title="LUD FS", layout="wide")
ss = st.session_state

# 1. TEMA (Oscuro por defecto)
if 'tm' not in ss: ss.tm = "Oscuro"
bg, tx, cd = ("#1E1E1E","#FFF","#2D2D2D") if ss.tm=="Oscuro" else ("#FFF","#000","#F0F2F6")

st.markdown(f"""<style>
    .stApp {{background:{bg};}}
    h1,h2,h3,p,b,span,div {{color:{tx}!important;}}
    .reloj {{font-size:50px;color:#7A0019;text-align:center;font-weight:bold;}}
    [data-testid="stVerticalBlockBorderWrapper"] {{background:{cd};border-radius:10px;padding:10px;}}
    .stButton>button {{width:100%; border-radius:8px; font-weight:bold;}}
</style>""", unsafe_allow_html=True)

# 2. DATA
if 'js' not in ss:
    ss.js = [{"id":i,"n":f"J{i+1}","t1":0.0,"t2":0.0,"ini":None,"p":False,"e":0,"g":0,"t":0,"per":0,"rec":0} for i in range(14)]
if 'rt1' not in ss: ss.rt1, ss.rt2, ss.pt = 0.0, 0.0, "T1"
if 'ml' not in ss: ss.ml, ss.mr, ss.fl, ss.fr = 0, 0, 0, 0
if 'ac' not in ss: ss.ac, ss.ig = False, None

# 3. CABECERA
c_h1, c_h2 = st.columns([3, 1])
with c_h1: st.title("🐸 LUD FS Match Center")
with c_h2: ss.tm = st.selectbox("Apariencia:", ["Oscuro", "Claro"])

c1, c2, c3 = st.columns(3)
with c1:
    st.write(f"### LUD: {ss.ml}")
    if st.button("⚽ +GOL"): ss.ml+=1; st.rerun()
    st.write(f"Faltas: {ss.fl}")
    if st.button("+FALTA"): ss.fl+=1; st.rerun()
with c2:
    ss.pt = st.radio("Tiempo:",["T1","T2"], horizontal=True)
    if st.button("🔄 RESET"): ss.clear(); st.rerun()
with c3:
    st.write(f"### RIV: {ss.mr}")
    if st.button("⚽ +GOL RIV"): ss.mr+=1; st.rerun()
    st.write(f"Faltas: {ss.fr}")
    if st.button("+FR RIVAL"): ss.fr+=1; st.rerun()

st.divider()

# 4. RELOJ GLOBAL
tg = ss.rt1 if ss.pt=="T1" else ss.rt2
if ss.ac and ss.ig: tg += time.time()-ss.ig
m, s = divmod(int(tg), 60)

cx, cy = st.columns(2)
with cx:
    if not ss.ac:
        if st.button("▶ START", type="primary"):
            ss.ac, now = True, time.time()
            ss.ig = now
            for j in ss.js:
                if j["p"]: j["ini"] = now
            st.rerun()
    else:
        if st.button("⏸ STOP", type="secondary"):
            ss.ac, now = False, time.time()
            if ss.pt=="T1": ss.rt1 += now-ss.ig
            else: ss.rt2 += now-ss.ig
            for j in ss.js:
                if j["p"] and j["ini"]:
                    if ss.pt=="T1": j["t1"]+=now-j["ini"]
                    else: j["t2"]+=now-j["ini"]
                    j["ini"] = None
            ss.ig = None; st.rerun()
with cy: st.markdown(f"<p class='reloj'>{m:02d}:{sg if (sg:=s) else '00'}</p>", unsafe_allow_html=True)

# 5. JUGADORES (2 COLUMNAS)
ep = sum(1 for j in ss.js if j["p"])
st.write(f"**Pista: {ep}/5**")

for i in range(0, 14, 2):
    cols = st.columns(2)
    for idx, col in enumerate(cols):
        ji = i + idx
        if ji >= 14: break
        j = ss.js[ji]
        with col:
            with st.container(border=True):
                j["n"] = st.text_input("Nom:", j["n"], key=f"n{ji}", label_visibility="collapsed")
                tj = j["t1"] if ss.pt=="T1" else j["t2"]
                if ss.ac and j["p"] and j["ini"]: tj += time.time()-j["ini"]
                mm, ss_j = divmod(int(tj), 60)
                st.write(f"⏱ **{mm:02d}:{ss_j:02d}** | ⚽ **{j['g']}**")
                
                # Botones Scouting
                ba, bb, bc = st.columns(3)
                if ba.button(f"🎯{j['t']}", key=f"t{ji}"): j["t"]+=1; st.rerun()
                if bb.button(f"⚠️{j['per']}", key=f"p{ji}"): j["per"]+=1; st.rerun()
                if bc.button(f"🛡️{j['rec']}", key=f"r{ji}"): j["rec"]+=1; st.rerun()
                
                # Entrada/Salida y Gol
                bgol, bch = st.columns([1, 2])
                if bgol.button("⚽", key=f"go{ji}"): j["g"]+=1; ss.ml+=1; st.rerun()
                
                txt = "SALIR 🔴" if j["p"] else "ENTRAR 🟢"
                if bch.button(txt, key=f"en{ji}"):
                    now = time.time()
                    if not j["p"] and ep < 5:
                        j["p"], j["e"] = True, j["e"]+1
                        if ss.ac: j["ini"] = now
                        st.rerun()
                    elif j["p"]:
                        if ss.ac and j["ini"]:
                            if ss.pt=="T1": j["t1"]+=now-j["ini"]
                            else: j["t2"]+=now-j["ini"]
                        j["p"], j["ini"] = False, None; st.rerun()
                    else: st.toast("Max 5!")

st.divider()
if st.button("💾 EXCEL"):
    df = pd.DataFrame(ss.js)
    st.download_button("Bajar", df.to_csv().encode('utf-8'), "lud.csv")
