import streamlit as st
import pandas as pd
import time

st.set_page_config(page_title="LUD", layout="wide")
ss = st.session_state

# 1. TEMA
if 'tm' not in ss: ss.tm = "Oscuro"
bg, tx = ("#1E1E1E","#FFF") if ss.tm=="Oscuro" else ("#FFF","#000")
st.markdown(f"<style>.stApp{{background:{bg};}} h1,h2,h3,p,b,span{{color:{tx}!important;}} .reloj{{font-size:50px;color:red;text-align:center;}}</style>",unsafe_allow_html=True)

# 2. DATA
if 'js' not in ss:
    ss.js = [{"id":i,"n":f"J{i+1}","t1":0.0,"t2":0.0,"ini":None,"p":False,"e":0,"g":0,"t":0,"per":0,"rec":0} for i in range(14)]
if 'rt1' not in ss: ss.rt1, ss.rt2, ss.pt = 0.0, 0.0, "T1"
if 'ml' not in ss: ss.ml, ss.mr, ss.fl, ss.fr = 0, 0, 0, 0
if 'ac' not in ss: ss.ac, ss.ig = False, None

# 3. INTERFAZ SUPERIOR
ss.tm = st.selectbox("Modo:", ["Oscuro", "Claro"])
st.write(f"LUD: {ss.ml} | RIV: {ss.mr} | PARTE: {ss.pt}")

if st.button("+GOL LUD"): ss.ml+=1; st.rerun()
if st.button("+FALTA LUD"): ss.fl+=1; st.rerun()
ss.pt = st.radio("Parte:",["T1","T2"], horizontal=True)

# 4. RELOJ
tg = ss.rt1 if ss.pt=="T1" else ss.rt2
if ss.ac and ss.ig: tg += time.time()-ss.ig
m, s = divmod(int(tg), 60)
st.markdown(f"<p class='reloj'>{m:02d}:{s:02d}</p>", unsafe_allow_html=True)

if not ss.ac:
    if st.button("▶ START"):
        ss.ac, now = True, time.time()
        ss.ig = now
        for j in ss.js:
            if j["p"]: j["ini"] = now
        st.rerun()
else:
    if st.button("⏸ STOP"):
        ss.ac, now = False, time.time()
        if ss.pt=="T1": ss.rt1 += now-ss.ig
        else: ss.rt2 += now-ss.ig
        for j in ss.js:
            if j["p"] and j["ini"]:
                if ss.pt=="T1": j["t1"]+=now-j["ini"]
                else: j["t2"]+=now-j["ini"]
                j["ini"] = None
        ss.ig = None; st.rerun()

# 5. JUGADORES
ep = sum(1 for j in ss.js if j["p"])
st.write(f"En pista: {ep}/5")

for i, j in enumerate(ss.js):
    with st.expander(f"{j['n']} - {int(j['t1']+j['t2'])}s"):
        j["n"] = st.text_input("Nom:", j["n"], key=f"n{i}")
        if st.button(f"🎯 Tiros: {j['t']}", key=f"t{i}"): j["t"]+=1; st.rerun()
        if st.button(f"⚠️ Perd: {j['per']}", key=f"p{i}"): j["per"]+=1; st.rerun()
        if st.button(f"🛡️ Rec: {j['rec']}", key=f"r{i}"): j["rec"]+=1; st.rerun()
        if st.button(f"⚽ GOL", key=f"g{i}"): j["g"]+=1; ss.ml+=1; st.rerun()
        
        txt = "SALIR 🔴" if j["p"] else "ENTRAR 🟢"
        if st.button(txt, key=f"e{i}"):
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

# 6. EXPORT
if st.button("💾 EXCEL"):
    df = pd.DataFrame(ss.js)
    st.download_button("Bajar", df.to_csv().encode('utf-8'), "lud.csv")
if st.button("🔄 RESET"): ss.clear(); st.rerun()
