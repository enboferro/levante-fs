import streamlit as st
import time

# Configuración de página para iPad 10" (Landscape)
st.set_page_config(page_title="LUD FUTSAL PRO - iPad", layout="wide")

st.markdown("""
    <style>
    .block-container { padding: 0.5rem 1rem; background-color: #f0f2f6; }
    
    /* Cronómetro Hiper-Gigante */
    .main-clock { 
        font-size: 140px !important; 
        font-weight: 900; 
        text-align: center; 
        line-height: 0.9; 
        color: #1d1d1d;
        font-family: 'Courier New', Courier, monospace;
        background: white;
        border-radius: 15px;
        padding: 10px;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
    }
    
    .score-val { font-size: 90px; font-weight: 900; text-align: center; line-height: 1; }
    
    /* Pista de Fútbol Sala 40x20 */
    .pitch-futsal {
        background-color: #1a4a7a; /* Color azul pista oficial LNFS */
        border: 4px solid white;
        height: 380px;
        position: relative;
        border-radius: 5px;
        margin: 10px 0;
        display: flex;
        flex-direction: column;
    }
    
    /* Botones de Jugador Estilo iPad (Grandes y limpios) */
    div.stButton > button { 
        height: 90px !important; 
        font-size: 20px !important; 
        font-weight: bold !important;
        border-radius: 10px;
        box-shadow: 1px 1px 5px rgba(0,0,0,0.1);
    }
    
    /* Marcadores de zona */
    .zone-btn { font-size: 14px !important; height: 50px !important; }
    </style>
    """, unsafe_allow_html=True)

# --- INICIALIZACIÓN ---
if 'players_stats' not in st.session_state:
    jugadores = ["Serra", "Julian", "Omar", "Tony", "Rochina", "Benages", "Pedrito", "Parre Jr", "Baeza", "Manu", "Pedro Toro", "Paco Silla", "Jose", "Coque", "Nacho Gomez"]
    st.session_state.players_stats = {nom: {'total': 0, 'current_shift': 0, 'last_entry': None, 'in_pista': False} for nom in jugadores}
    st.session_state.update({
        'running': False, 'tiempo_acumulado': 0, 'ultimo_click': None, 
        'goles_lud': 0, 'goles_riv': 0, 
        'mapa_futsal': {"LUD-Ataque": 0, "LUD-Contra": 0, "RIV-Ataque": 0, "RIV-Contra": 0}
    })

s = st.session_state

# --- LÓGICA CRONO ---
if s.running:
    ahora = time.time()
    tiempo_actual = s.tiempo_acumulado + (ahora - s.ultimo_click)
    for p, stats in s.players_stats.items():
        if stats['in_pista']: stats['current_shift'] = ahora - stats['last_entry']
else:
    tiempo_actual = s.tiempo_acumulado
mins, secs = divmod(int(tiempo_actual), 60)

# --- LAYOUT DASHBOARD IPAD ---
col_stats, col_control = st.columns([1, 1.2])

with col_stats:
    # MARCADOR Y TIEMPO
    st.markdown(f"<div class='main-clock'>{mins:02d}:{secs:02d}</div>", unsafe_allow_html=True)
    
    m1, m2, m3 = st.columns([1, 1, 1])
    with m1:
        st.markdown(f"<div class='score-val'>{s.goles_lud}</div><p style='text-align:center; font-weight:bold;'>LUD</p>", unsafe_allow_html=True)
    with m2:
        if st.button("▶️ / ⏸️", use_container_width=True):
            if not s.running:
                s.running = True; s.ultimo_click = time.time()
                for p in s.players_stats.values():
                    if p['in_pista']: p['last_entry'] = s.ultimo_click
            else:
                s.running = False; s.tiempo_acumulado += (time.time() - s.ultimo_click)
                for p in s.players_stats.values():
                    if p['in_pista']: p['total'] += p['current_shift']; p['current_shift'] = 0
            st.rerun()
    with m3:
        st.markdown(f"<div class='score-val'>{s.goles_riv}</div><p style='text-align:center; font-weight:bold;'>RIVAL</p>", unsafe_allow_html=True)

    st.markdown("### 🏟️ MAPA DE GOLES (40x20)")
    # Representación de la pista con botones de zona
    st.markdown("<div class='pitch-futsal'>", unsafe_allow_html=True)
    z1, z2 = st.columns(2)
    with z1:
        st.write("**NUESTRO CAMPO**")
        if st.button("⚽ GOL LUD (Contra)", key="l_contra"): 
            s.goles_lud += 1; s.mapa_futsal["LUD-Contra"] += 1; st.rerun()
        if st.button("⚠️ RIVAL (Ataque)", key="r_ataque"): 
            s.goles_riv += 1; s.mapa_futsal["RIV-Ataque"] += 1; st.rerun()
    with z2:
        st.write("**CAMPO RIVAL**")
        if st.button("⚽ GOL LUD (Posicional)", key="l_pos"): 
            s.goles_lud += 1; s.mapa_futsal["LUD-Ataque"] += 1; st.rerun()
        if st.button("⚠️ RIVAL (Contra)", key="r_contra"): 
            s.goles_riv += 1; s.mapa_futsal["RIV-Contra"] += 1; st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.info(f"Análisis: Goles Posicionales: {s.mapa_futsal['LUD-Ataque']} | Goles Contra: {s.mapa_futsal['LUD-Contra']}")

with col_control:
    st.markdown(f"### 🏃 ROTACIONES (4+1)")
    p_campo = [p for p, stt in s.players_stats.items() if stt['in_pista'] and p not in ["Serra", "Jose"]]
    st.write(f"Jugadores de campo en pista: **{len(p_campo)} / 4**")
    
    # Cuadrícula de jugadores (2 columnas para que los botones sean gigantes en iPad)
    p_cols = st.columns(2)
    for i, (nom, stats) in enumerate(s.players_stats.items()):
        with p_cols[i % 2]:
            t_total = stats['total'] + (stats['current_shift'] if s.running and stats['in_pista'] else 0)
            m_t, s_t = divmod(int(t_total), 60)
            m_c, s_c = divmod(int(stats['current_shift']), 60)
            
            # Formato de tiempo PRO
            label = f"{nom}\nTotal: {m_t:02d}:{s_t:02d} | Shift: {m_c:02d}:{s_c:02d}"
            
            if st.button(label, key=f"btn_{nom}", type="primary" if stats['in_pista'] else "secondary"):
                if not stats['in_pista']:
                    if nom in ["Serra", "Jose"] or len(p_campo) < 4:
                        stats['in_pista'] = True; stats['last_entry'] = time.time() if s.running else None
                else:
                    stats['in_pista'] = False
                    if s.running and stats['last_entry']: stats['total'] += (time.time() - stats['last_entry'])
                    stats['current_shift'] = 0
                st.rerun()
    
    if st.button("🔄 RESET TODO", use_container_width=True): st.session_state.clear(); st.rerun()

if s.running:
    time.sleep(1)
    st.rerun()
