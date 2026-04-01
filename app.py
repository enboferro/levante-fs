import streamlit as st
import pandas as pd
import time
from streamlit_autorefresh import st_autorefresh

# Configuración de página
st.set_page_config(page_title="LUD FS - Match Center", layout="wide", page_icon="🐸")

# Autorefresh cada 1 segundo
st_autorefresh(interval=1000, key="futsalrefresh")

ss = st.session_state

# --- ESTILOS PERSONALIZADOS LUD ---
st.markdown("""
    <style>
    .stApp { background-color: #F8F9FA; }
    .main-header { background-color: #7A0019; padding: 20px; border-radius: 15px; color: white; margin-bottom: 20px; }
    .reloj-box { background-color: white; border: 3px solid #7A0019; border-radius: 20px; padding: 10px; }
    .card-jugador { background-color: white; border-left: 8px solid #003D7A; border-radius: 10px; padding: 15px; box-shadow: 2px 2px 10px rgba(0,0,0,0.1); }
    .stButton>button { border-radius: 8px; font-weight: bold; transition: 0.3s; }
    h1, h2, h3 { color: #003D7A !important; }
    </style>
    """, unsafe_allow_html=True)

# 1. INICIALIZACIÓN
if 'js' not in ss:
    ss.js = [{"id":i,"n":f"Jugador {i+1}","t1":0.0,"t2":0.0,"ini":None,"p":False,"e":0,"g":0,"t":0,"per":0,"rec":0} for i in range(14)]
if 'rt1' not in ss: ss.rt1, ss.rt2, ss.pt = 0.0, 0.0, "T1"
if 'ml' not in ss: ss.ml, ss.mr, ss.fl, ss.fr = 0, 0, 0, 0
if 'ac' not in ss: ss.ac, ss.ig = False, None

# 2. CABECERA CON ESCUDO
with st.container():
    col_esc, col_tit, col_res = st.columns([1, 4, 1])
    with col_esc:
        # Intenta cargar el escudo si existe en GitHub, si no, usa el emoji de la rana
        st.image("https://upload.wikimedia.org/wikipedia/en/thumb/7/7b/Levante_Uni%C3%B3n_Deportiva%2C_S.A.D._logo.svg/1200px-Levante_Uni%C3%B3n_Deportiva%2C_S.A.D._logo.svg.png", width=80)
    with col_tit:
        st.title("LEVANTE UD FS")
        st.caption("Panel Oficial de Control de Partido")
    with col_res:
        if st.button("🔄 RESET"): ss.clear(); st.rerun()

# 3. MARCADOR Y RELOJ CENTRAL
with st.container():
    m_col1, m_col2, m_col3 = st.columns([2, 2, 2])
    
    with m_col1:
        st.markdown(f"<div style='text-align:center; background:#003D7A; color:white; padding:10px; border-radius:10px;'><h2>LUD: {ss.ml}</h2></div>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        if c1.button("⚽ GOL LUD", use_container_width=True): ss.ml+=1; st.rerun()
        if c2.button(f"⚠️ FALTA ({ss.fl})", use_container_width=True): ss.fl+=1; st.rerun()

    with m_col2:
        # RELOJ EFECTIVO
        tg = ss.rt1 if ss.pt=="T1" else ss.rt2
        if ss.ac and ss.ig: tg += time.time() - ss.ig
        m, s = divmod(int(tg), 60)
        
        st.markdown(f"<div class='reloj-box'><h1 style='text-align:center; color:#7A0019; margin:0;'>{m:02d}:{s:02d}</h1></div>", unsafe_allow_html=True)
        
        ss.pt = st.radio("Periodo:", ["T1", "T2"], horizontal=True, label_visibility="collapsed")
        if not ss.ac:
            if st.button("▶ INICIAR TIEMPO", type="primary", use_container_width=True):
                ss.ac, now = True, time.time()
                ss.ig = now
                for j in ss.js:
                    if j["p"]: j["ini"] = now
                st.rerun()
        else:
            if st.button("⏸ PARAR TIEMPO", type="secondary", use_container_width=True):
                ss.ac, now = False, time.time()
                if ss.pt=="T1": ss.rt1 += now - ss.ig
                else: ss.rt2 += now - ss.ig
                for j in ss.js:
                    if j["p"] and j["ini"]:
                        if ss.pt=="T1": j["t1"] += now - j["ini"]
                        else: j["t2"] += now - j["ini"]
                        j["ini"] = None
                ss.ig = None; st.rerun()

    with m_col3:
        st.markdown(f"<div style='text-align:center; background:#7A0019; color:white; padding:10px; border-radius:10px;'><h2>RIVAL: {ss.mr}</h2></div>", unsafe_allow_html=True)
        c3, c4 = st.columns(2)
        if c3.button("⚽ GOL RIV", use_container_width=True): ss.mr+=1; st.rerun()
        if c4.button(f"⚠️ FALTA ({ss.fr})", use_container_width=True): ss.fr+=1; st.rerun()

# 4. PISTA Y JUGADORES
st.divider()
ep = sum(1 for j in ss.js if j["p"])
st.subheader(f"👥 Jugadores en pista: {ep} / 5")

for i in range(0, 14, 2):
    cols = st.columns(2)
    for idx, col in enumerate(cols):
        ji = i + idx
        if ji >= 14: break
        j = ss.js[ji]
        with col:
            # Lógica Semáforo Fatiga
            t_tramo = (time.time() - j["ini"]) if (j["p"] and j["ini"] and ss.ac) else 0
            color_f = "⚪"
            if t_tramo > 360: color_f = "🔴"
            elif t_tramo > 240: color_f = "🟡"
            elif j["p"]: color_f = "🟢"

            with st.container():
                st.markdown(f"<div style='background:white; padding:15px; border-radius:10px; border-left: 8px solid {'#90EE90' if j['p'] else '#D3D3D3'}; box-shadow: 2px 2px 5px rgba(0,0,0,0.05);'>", unsafe_allow_html=True)
                
                c_n, c_t = st.columns([2, 1])
                j["n"] = c_n.text_input("Nombre", j["n"], key=f"n{ji}", label_visibility="collapsed")
                
                tj = j["t1"] if ss.pt=="T1" else j["t2"]
                if ss.ac and j["p"] and j["ini"]: tj += time.time() - j["ini"]
                mm, ss_j = divmod(int(tj), 60)
                c_t.markdown(f"**{color_f} {mm:02d}:{ss_j:02d}**")
                
                # Botones Scouting con Iconos
                s1, s2, s3, s4 = st.columns(4)
                if s1.button(f"🎯{j['t']}", key=f"t{ji}"): j["t"]+=1; st.rerun()
                if s2.button(f"⚠️{j['per']}", key=f"p{ji}"): j["per"]+=1; st.rerun()
                if s3.button(f"🛡️{j['rec']}", key=f"r{ji}"): j["rec"]+=1; st.rerun()
                if s4.button(f"⚽{j['g']}", key=f"g{ji}"): j["g"]+=1; ss.ml+=1; st.rerun()
                
                # Cambio
                txt = "🔴 SALIR" if j["p"] else "🟢 ENTRAR"
                if st.button(txt, key=f"en{ji}", use_container_width=True):
                    now = time.time()
                    if not j["p"] and ep < 5:
                        j["p"], j["e"] = True, j["e"]+1
                        if ss.ac: j["ini"] = now
                        st.rerun()
                    elif j["p"]:
                        if ss.ac and j["ini"]:
                            if ss.pt=="T1": j["t1"] += now - j["ini"]
                            else: j["t2"] += now - j["ini"]
                        j["p"], j["ini"] = False, None; st.rerun()
                    else: st.toast("¡Máximo 5 jugadores!", icon="🚫")
                
                st.markdown("</div>", unsafe_allow_html=True)

# 5. EXPORTACIÓN
st.divider()
if st.button("💾 DESCARGAR INFORME FINAL (CSV)", use_container_width=True):
    df = pd.DataFrame([{"Jugador":x["n"],"Minutos":round((x["t1"]+x["t2"])/60,1),"Goles":x["g"],"Tiros":x["t"],"Perdidas":x["per"],"Recup":x["rec"]} for x in ss.js])
    st.download_button("Click para descargar", df.to_csv(index=False).encode('utf-8'), "LUD_FS_Stats.csv", "text/csv")
