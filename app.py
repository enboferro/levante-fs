import streamlit as st
import pandas as pd
import time
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="LUD Match Control v22.0", layout="wide")

# --- CSS MEJORADO ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@700&family=Roboto:wght@400;700;900&display=swap');
    html, body, [class*="css"] { font-family: 'Roboto', sans-serif; background-color: #e0e0e0; }
    .block-container { padding: 0.1rem !important; }
    .stTabs [data-baseweb="tab-list"] { gap: 20px; justify-content: center; }
    .stTabs [data-baseweb="tab"] { height: 50px; background-color: #4B2E2A; color: white; border-radius: 10px 10px 0 0; padding: 10px 20px; }
    
    /* Estilos Scoreboard y Jugadores (Iguales a v21.1) */
    .scoreboard-container { display: flex; align-items: center; justify-content: space-around; background: #4B2E2A; padding: 5px; border-radius: 15px; color: white; margin-top: 5px; border-bottom: 4px solid #000; }
    .score-number { font-size: 4rem !important; font-weight: 900; font-family: 'Roboto Mono'; }
    .stadium-clock { font-family: 'Roboto Mono'; font-size: 4.5rem !important; font-weight: 700; text-align: center; }
    .pista-portero { background-color: #008080 !important; color: white; border-radius: 8px; padding: 2px; text-align: center; font-weight: 900; border: 2px solid white; }
    .pista-verde { background-color: #00FF41 !important; color: #000; border-radius: 8px; padding: 2px; text-align: center; font-weight: 900; }
    .pista-naranja { background-color: #FF5E00 !important; color: white; border-radius: 8px; padding: 2px; text-align: center; font-weight: 900; border: 1px solid white; }
    .pista-roja { background-color: #FF0000 !important; color: white; border-radius: 8px; padding: 2px; text-align: center; font-weight: 900; border: 2px solid #FFFF00; animation: blinker 0.8s linear infinite; }
    .banquillo { background-color: #444444 !important; color: white; border-radius: 8px; padding: 2px; text-align: center; opacity: 0.9; }
    @keyframes blinker { 50% { opacity: 0.4; } }
    </style>
    """, unsafe_allow_html=True)

# --- ESTADO DE SESIÓN ---
if 'js' not in st.session_state:
    n = ["Serra","Julian","Omar","Tony","Rochina","Benages","Pedrito","Parre Jr","Baeza","Manu","Pedro Toro","Paco Silla","Jose","Coque","Nacho Gomez"]
    st.session_state.update({
        "js": [{"n":x,"tt":0.0,"tot":0.0,"r":0,"i":None,"p":False} for x in n],
        "eventos": [], "pm": 0, "pp": 0, "al": 0, "rl": 0, "ar": 0, "rr": 0, 
        "ml": 0, "mr": 0, "fl": 0, "fr": 0, "ta": 0.0, "ic": None, "on": False, 
        "pa": "1T", "rv": "RIVAL", "tm": False, "tm_i": None,
        "analisis_goles": [] # <--- NUEVA BASE DE DATOS TÁCTICA
    })

s = st.session_state
st_autorefresh(1000, key="f5_lud_v22")

# --- LÓGICA DE TIEMPO ---
ah = time.time()
tr_total = s.ta + (ah - s.ic if s.on and s.ic else 0)
if tr_total >= 1200 and s.on: # Auto-stop
    tr_total = 1200; s.ta = 1200; s.on, s.ic = False, None
    for j in s.js:
        if j["p"] and j["i"]: d = time.time()-j["i"]; j["tot"]+=d; j["tt"]+=d; j["i"]=None
    st.rerun()

rem = max(0, 1200 - tr_total)
min_act = int(tr_total // 60)

# --- PESTAÑAS ---
tab1, tab2 = st.tabs(["🎮 CONTROL PARTIDO", "📊 ANÁLISIS TÁCTICO"])

with tab1:
    # Título y Reloj (Tu diseño actual)
    st.markdown(f'<div style="text-align:center;"><img src="https://upload.wikimedia.org/wikipedia/en/thumb/7/7b/Levante_Uni%C3%B3n_Deportiva%2C_S.A.D._logo.svg/1200px-Levante_Uni%C3%B3n_Deportiva%2C_S.A.D._logo.svg.png" width="30"><span style="font-size:1.2rem; font-weight:900; color:#4B2E2A; margin-left:10px;">MATCH CONTROL BY KIKE</span></div>', unsafe_allow_html=True)
    
    mv, sv = divmod(int(rem), 60)
    tm_sec = max(0, 60 - int(ah - s.tm_i)) if s.tm and s.tm_i else 0
    timer_display = f"{tm_sec}s" if s.tm else f"{mv:02d}:{sv:02d}"

    st.markdown(f"""
        <div class="scoreboard-container">
            <div style="text-align:center;"><div class="score-number">{s.ml}</div><div style="font-size:0.8rem; font-weight:900;">LEVANTE UD</div></div>
            <div class="stadium-clock" style="color: {'#FF0000' if rem <= 0 else '#FFFFFF'};">{timer_display}</div>
            <div style="text-align:center;"><div class="score-number">{s.mr}</div><div style="font-size:0.8rem; font-weight:900;">{s.rv[:8]}</div></div>
        </div>
        """, unsafe_allow_html=True)

    # Botones Start/Stop
    c_bt = st.columns(3)
    if c_bt[0].button("▶ START / STOP ⏸", key="tm_main"):
        if tr_total < 1200:
            if not s.on:
                s.ic, s.on, s.tm = time.time(), True, False
                for j in s.js: 
                    if j["p"]: j["i"] = s.ic
            else:
                now = time.time(); s.ta += now - s.ic; s.on, s.ic = False, None
                for j in s.js:
                    if j["p"] and j["i"]: d = now-j["i"]; j["tot"]+=d; j["tt"]+=d; j["i"]=None
            st.rerun()

    # --- LÓGICA DE CAPTURA DE CUARTETO ---
    def registrar_gol(tipo, autor):
        # Filtrar jugadores en pista que NO sean porteros
        cuarteto = [j['n'] for j in s.js if j['p'] and j['n'] not in ["Serra", "Jose"]]
        # Rellenar si hay menos de 4 por alguna razón
        while len(cuarteto) < 4: cuarteto.append("-")
        
        s.analisis_goles.append({
            "Minuto": f"{mv:02d}:{sv:02d}",
            "Tipo": tipo,
            "Autor/Dorsal": autor,
            "Marcador": f"{s.ml}-{s.mr}",
            "Jugador 1": cuarteto[0],
            "Jugador 2": cuarteto[1],
            "Jugador 3": cuarteto[2],
            "Jugador 4": cuarteto[3]
        })

    # Goles
    c_goles = st.columns(4)
    with c_goles[0]:
        with st.popover("⚽ GOL LUD", use_container_width=True):
            p_gol = st.selectbox("Autor", [j['n'] for j in s.js])
            if st.button("CONFIRMAR GOL LUD"):
                s.ml += 1
                registrar_gol("LUD", p_gol)
                s.eventos.append({'min':min_act,'info':f'⚽{p_gol}'})
                st.rerun()
    with c_goles[1]:
        with st.popover("⚽ GOL RIVAL", use_container_width=True):
            d_gol = st.number_input("Dorsal", 1, 99)
            if st.button("CONFIRMAR GOL RIVAL"):
                s.mr += 1
                registrar_gol("RIVAL", f"#{d_gol}")
                s.eventos.append({'min':min_act,'info':f'⚽#{d_gol} RIV'})
                st.rerun()

    # --- RESTO DE INTERFAZ (Jugadores y Footer) ---
    # (Se mantiene igual que la v21.1 para no perder funcionalidad)
    cols = st.columns(6)
    for i, j in enumerate(s.js):
        with cols[i%6]:
            cur_sec = j["tt"] + (ah-j["i"] if s.on and j["p"] and j["i"] else 0)
            tot_sec = j["tot"] + (ah-j["i"] if s.on and j["p"] and j["i"] else 0)
            if not j['p']: cl = "banquillo"
            elif j['n'] in ["Serra", "Jose"]: cl = "pista-portero"
            else:
                if cur_sec < 240: cl = "pista-verde"
                elif cur_sec < 360: cl = "pista-naranja"
                else: cl = "pista-roja"
            st.markdown(f"<div class='{cl}'>", unsafe_allow_html=True)
            mc, vc = divmod(int(cur_sec), 60); mt, vt = divmod(int(tot_sec), 60)
            st.markdown(f"<div style='font-size:0.8rem;'>{j['n']}</div><div style='font-size:1.2rem; font-weight:900;'>{mc:02d}:{vc:02d}</div><div style='font-size:0.6rem;'>Σ{mt:02d}:{vt:02d} | R:{j['r']}</div>", 1)
            if st.button("🔄", key=f"c_{i}", use_container_width=True):
                if not j["p"] and sum(1 for x in s.js if x["p"]) < 5:
                    j["p"], j["i"], j["r"] = True, (ah if s.on else None), j["r"]+1; j["tt"] = 0.0
                elif j["p"]:
                    if s.on and j["i"]: d = ah-j["i"]; j["tot"]+=d; j["tt"]+=d
                    j["p"], j["i"] = False, None
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

with tab2:
    st.subheader("📋 Registro de Cuartetos en Goles")
    if s.analisis_goles:
        df_goles = pd.DataFrame(s.analisis_goles)
        st.table(df_goles) # Tabla fija para lectura rápida
        
        # Opcional: Análisis de eficiencia
        st.info("💡 Consejo: Los jugadores que más aparecen en los goles LUD son tu 'Cuarteto de Oro'.")
    else:
        st.write("Aún no se han registrado goles en este partido.")

# Footer simétrico (Simplificado para el ejemplo pero funcional)
st.markdown("---")
f_cols = st.columns([2,4,2])
with f_cols[0]: st.button(f"Faltas LUD: {s.fl}", on_click=lambda: setattr(s, 'fl', s.fl+1))
with f_cols[2]: st.button(f"Faltas Rival: {s.fr}", on_click=lambda: setattr(s, 'fr', s.fr+1))
