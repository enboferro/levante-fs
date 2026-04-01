import streamlit as st
import pandas as pd
import time

st.set_page_config(page_title="LUD PRO SCORER", layout="wide")
# Estilo para que todo sea legible y profesional
st.markdown("<style>h1,h2,h3,p,b{color:black!important;font-weight:bold;} .reloj{font-size:45px;color:#7A0019;text-align:center;}</style>",unsafe_allow_html=True)

ss = st.session_state

# 1. Inicialización
if 'js' not in ss:
    ss.js = [{"id":i,"n":f"J{i+1}","t1":0.0,"t2":0.0,"ini":None,"p":False,"e":0,"g":0,"t":0,"per":0,"rec":0} for i in range(14)]
if 'rt1' not in ss: ss.rt1 = 0.0
if 'rt2' not in ss: ss.rt2 = 0.0
if 'pt' not in ss: ss.pt = "T1"
if 'ml' not in ss: ss.ml = 0
if 'mr' not in ss: ss.mr = 0
if 'fl' not in ss: ss.fl = 0
if 'fr' not in ss: ss.fr = 0
if 'ac' not in ss: ss.ac = False
if 'ig' not in ss: ss.ig = None

# 2. Marcador y Faltas
c1, c2, c3 = st.columns(3)
with c1:
    st.subheader(f"LUD: {ss.ml}")
    if st.button("⚽ +1 GOL LUD"): ss.ml+=1; st.rerun()
    st.write(f"⚠️ Faltas: {ss.fl}")
    if st.button("➕ AÑADIR FALTA"): ss.fl+=1; st.rerun()
with c2:
    ss.pt = st.radio("Tiempo:",["T1","T2"], horizontal=True)
    if st.button("🔄 REINICIAR"): ss.clear(); st.rerun()
with c3:
    st.subheader(f"RIV: {ss.mr}")
    if st.button("⚽ +1 GOL RIVAL"): ss.mr+=1; st.rerun()
    st.write(f"⚠️ Faltas: {ss.fr}")
    if st.button("➕ FALTA RIVAL"): ss.fr+=1; st.rerun()

st.divider()

# 3. Reloj Efectivo
tg = ss.rt1 if ss.pt=="T1" else ss.rt2
if ss.ac and ss.ig is not None: tg += time.time() - ss.ig
mg, sg = divmod(int(tg), 60)

cx, cy = st.columns(2)
with cx:
    if not ss.ac:
        if st.button("▶ START (Tiempo Juego)", type="primary", use_container_width=True):
            ss.ac, now = True, time.time()
            ss.ig = now
            for j in ss.js:
                if j["p"]: j["ini"] = now
            st.rerun()
    else:
        if st.button("⏸ STOP (Balón Parado)", type="secondary", use_container_width=True):
            ss.ac, now = False, time.time()
            if ss.pt=="T1": ss.rt1 += now - ss.ig
            else: ss.rt2 += now - ss.ig
            for j in ss.js:
                if j["p"] and j["ini"] is not None:
                    if ss.pt=="T1": j["t1"] += now - j["ini"]
                    else: j["t2"] += now - j["ini"]
                    j["ini"] = None
            ss.ig = None; st.rerun()
with cy:
    st.markdown(f"<p class='reloj'>{mg:02d}:{sg:02d}</p>", unsafe_allow_html=True)

# 4. Control de Pista (5 Jugadores)
ep = sum(1 for j in ss.js if j["p"])
if ep > 5: st.error(f"⚠️ ATENCIÓN: {ep} JUGADORES EN PISTA")
elif ep == 5: st.success("✅ QUINTETO CORRECTO")
else: st.warning(f"ℹ️ {ep} JUGADORES (Faltan {5-ep})")

# 5. Lista de Jugadores
for i in range(0, 14, 2):
    cols = st.columns(2)
    for idx, col in enumerate(cols):
        ji = i + idx
        if ji >= 14: break
        j = ss.js[ji]
        with col:
            with st.container(border=True):
                j["n"] = st.text_input("Nombre:", j["n"], key=f"n{ji}")
                tj = j["t1"] if ss.pt=="T1" else j["t2"]
                if ss.ac and j["p"] and j["ini"] is not None: tj += time.time() - j["ini"]
                m, s = divmod(int(tj), 60)
                st.write(f"⏱ {m:02d}:{s:02d} | ⚽ Goles: {j['g']}")
                
                # Estadísticas con nombres claros debajo
                ca, cb, cc = st.columns(3)
                if ca.button(f"🎯 {j['t']}", key=f"t{ji}"): j["t"]+=1; st.rerun()
                ca.caption("TIROS")
                
                if cb.button(f"⚠️ {j['per']}", key=f"p{ji}"): j["per"]+=1; st.rerun()
                cb.caption("PÉRDIDAS")
                
                if cc.button(f"🛡️ {j['rec']}", key=f"r{ji}"): j["rec"]+=1; st.rerun()
                cc.caption("RECUP.")
                
                st.write("") # Espaciador
                c_g, c_e = st.columns(2)
                if c_g.button("⚽ GOL", key=f"go{ji}", use_container_width=True): 
                    j["g"]+=1; ss.ml+=1; st.rerun()
                
                txt = "🔴 SALIR" if j["p"] else "🟢 ENTRAR"
                if c_e.button(txt, key=f"en{ji}", use_container_width=True):
                    now = time.time()
                    if not j["p"] and ep < 5:
                        j["p"], j["e"] = True, j["e"]+1
                        if ss.ac: j["ini"] = now
                        st.rerun()
                    elif j["p"]:
                        if ss.ac and j["ini"] is not None:
                            if ss.pt=="T1": j["t1"] += now - j["ini"]
                            else: j["t2"] += now - j["ini"]
                        j["p"], j["ini"] = False, None; st.rerun()
                    else: st.toast("¡Ya hay 5 jugadores!")

st.divider()
if st.button("💾 DESCARGAR EXCEL DE PARTIDO"):
    df = pd.DataFrame([{"Jugador":x["n"],"Minutos":round((x["t1"]+x["t2"])/60,1),"Goles":x["g"],"Tiros":x["t"],"Perdidas":x["per"],"Recup":x["rec"]} for x in ss.js])
    st.download_button("Descargar CSV", df.to_csv(index=False).encode('utf-8'), f"Stats_{int(time.time())}.csv", "text/csv")
