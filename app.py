import streamlit as st
import time

# Configuración de página para iPad 10" (Landscape)
st.set_page_config(page_title="LUD FUTSAL PRO - 14 Jugadores", layout="wide")

st.markdown("""
    <style>
    .block-container { padding: 0.5rem 1rem; }
    
    /* Cronómetro Ultra-Gigante */
    .main-clock { 
        font-size: 140px !important; font-weight: 900; text-align: center; 
        line-height: 0.9; color: #1d1d1d; font-family: monospace; 
    }
    .score-val { font-size: 110px; font-weight: 900; text-align: center; line-height: 1; }
    
    /* Botones de Jugador - Tamaño optimizado para 14 jugadores */
    div.stButton > button { 
        height: 110px !important; 
        border-radius: 15px;
        border: 2px solid #333;
    }
    
    /* Estilo para los nombres y TIEMPOS GRANDES */
    .player-name { font-size: 22px; font-weight: bold; margin-bottom: 5px; }
    .player-times { font-size: 20px; font-weight: 800; color: #cc0000; }
    
    /* Estilo de la pestaña de configuración */
    .stTextInput > div > div > input { font-size: 18px !important; }
    </style>
    """, unsafe_allow_html=True)

# --- INICIALIZACIÓN ---
if 'players_stats' not in st.session_state:
    # 14 jugadores iniciales (2 porteros + 12 de campo)
    default_players = ["Serra", "Jose", "Julian", "Omar", "Tony", "Rochina", "Benages", "Pedrito", "Parre Jr", "Baeza", "Manu", "Toro", "Silla", "Coque"]
    st.session_state.players_stats = {nom: {'total': 0, 'current_shift': 0, 'last_entry': None, 'in_pista': False} for nom in default_players}
    st.session_state.update({
        'running': False, 'tiempo_acumulado': 0, 'ultimo_click': None, 
        'goles_lud': 0, 'goles_riv': 0, 'porteros_nombres': ["Serra", "Jose"]
    })

s = st.session_state

# --- MENU DE PESTAÑAS ---
tab_partido, tab_config = st.tabs(["🎮 CONTROL DE PARTIDO", "⚙️ CONFIGURACIÓN PLANTILLA"])

# --- PESTAÑA 2: CONFIGURACIÓN (14 Jugadores) ---
with tab_config:
    st.subheader("Configura los 14 jugadores del acta")
    
    # Configurar quiénes son los porteros para la regla 4+1
    st.write("**Identifica a los 2 porteros (no cuentan en el cupo de 4 de campo):**")
    c_p1, c_p2 = st.columns(2)
    p1 = c_p1.selectbox("Portero 1", list(s.players_stats.keys()), index=0)
    p2 = c_p2.selectbox("Portero 2", list(s.players_stats.keys()), index=1)
    s.porteros_nombres = [p1, p2]

    st.divider()
    
    st.write("**Nombres de la plantilla:**")
    new_names = []
    cols_config = st.columns(2)
    current_list = list(s.players_stats.keys())
    
    for i in range(14):
        with cols_config[i % 2]:
            old_name = current_list[i] if i < len(current_list) else f"Jugador {i+1}"
            val = st.text_input(f"Posición {i+1}", value=old_name, key=f"cfg_{i}")
            new_names.append(val)
    
    if st.button("💾 GUARDAR CAMBIOS Y REINICIAR TIEMPOS"):
        new_stats = {name: {'total': 0, 'current_shift': 0, 'last_entry': None, 'in_pista': False} for name in new_names}
        s.players_stats = new_stats
        st.success("Plantilla actualizada. Tiempos puestos a cero.")
        st.rerun()

# --- PESTAÑA 1: PARTIDO ---
with tab_partido:
    # Lógica de cronómetros
    if s.running:
        ahora = time.time()
        tiempo_actual = s.tiempo_acumulado + (ahora - s.ultimo_click)
        for p, stats in s.players_stats.items():
            if stats['in_pista']: stats['current_shift'] = ahora - stats['last_entry']
    else:
        tiempo_actual = s.tiempo_acumulado
    
    mins, secs = divmod(int(tiempo_actual), 60)

    # --- CABECERA ---
    col_l, col_c, col_r = st.columns([1, 2, 1])
    with col_l:
        st.markdown(f"<div class='score-val'>{s.goles_lud}</div>", unsafe_allow_html=True)
        if st.button("⚽ GOL LUD", use_container_width=True): s.goles_lud += 1; st.rerun()
    with col_c:
        st.markdown(f"<div class='main-clock'>{mins:02d}:{secs:02d}</div>", unsafe_allow_html=True)
        ctrl1, ctrl2 = st.columns(2)
        if ctrl1.button("▶️ START / ⏸️ STOP", use_container_width=True):
            if not s.running:
                s.running = True; s.ultimo_click = time.time()
                for p in s.players_stats.values():
                    if p['in_pista']: p['last_entry'] = s.ultimo_click
            else:
                s.running = False; s.tiempo_acumulado += (time.time() - s.ultimo_click)
                for p in s.players_stats.values():
                    if p['in_pista']: p['total'] += p['current_shift']; p['current_shift'] = 0
            st.rerun()
        if ctrl2.button("🔄 RESET PARTIDO", use_container_width=True):
            s.update({'running': False, 'tiempo_acumulado': 0, 'ultimo_click': None, 'goles_lud': 0, 'goles_riv': 0})
            for p in s.players_stats.values(): p.update({'total': 0, 'current_shift': 0, 'last_entry': None, 'in_pista': False})
            st.rerun()
    with col_r:
        st.markdown(f"<div class='score-val'>{s.goles_riv}</div>", unsafe_allow_html=True)
        if st.button("⚽ GOL RIVAL", use_container_width=True): s.goles_riv += 1; st.rerun()

    st.divider()

    # --- JUGADORES (4+1) ---
    en_pista_campo = [p for p, stt in s.players_stats.items() if stt['in_pista'] and p not in s.porteros_nombres]
    st.markdown(f"### 🏃 Jugadores de campo: {len(en_pista_campo)} / 4")
    
    # Grid de 14 jugadores (2 columnas para iPad para que los botones sean masivos)
    cols_p = st.columns(2)
    for i, (nom, stats) in enumerate(s.players_stats.items()):
        with cols_p[i % 2]:
            # Cálculo de tiempos
            t_total = stats['total'] + (stats['current_shift'] if s.running and stats['in_pista'] else 0)
            m_t, s_t = divmod(int(t_total), 60)
            m_c, s_c = divmod(int(stats['current_shift']), 60)
            
            # Etiqueta interna con tiempos GRANDES
            label = f"{nom}  |  TOTAL {m_t:02d}:{s_t:02d}  |  SHIFT {m_c:02d}:{s_c:02d}"
            
            if st.button(label, key=f"btn_{nom}", type="primary" if stats['in_pista'] else "secondary"):
                if not stats['in_pista']:
                    if nom in s.porteros_nombres or len(en_pista_campo) < 4:
                        stats['in_pista'] = True
                        stats['last_entry'] = time.time() if s.running else None
                else:
                    stats['in_pista'] = False
                    if s.running and stats['last_entry']:
                        stats['total'] += (time.time() - stats['last_entry'])
                    stats['current_shift'] = 0
                st.rerun()

# Auto-refresco
if s.running:
    time.sleep(1)
    st.rerun()
