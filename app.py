import streamlit as st
import time

# 1. VOLVEMOS AL DISEÑO ORIGINAL DE LA VERSIÓN 30.0 (iPad 10" Landscape)
st.set_page_config(page_title="LUD FUTSAL - Versión 30.0", layout="wide")

st.markdown("""
    <style>
    .block-container { padding: 0.5rem 1rem; }
    
    /* Cronómetro Central de la Versión 30.0 */
    .main-clock { 
        font-size: 130px !important; font-weight: 900; text-align: center; 
        line-height: 1; color: #1d1d1d; font-family: monospace; 
        margin-bottom: 5px;
    }
    .score-val { font-size: 110px; font-weight: 900; text-align: center; line-height: 1; }
    
    /* BOTONES ORIGINALES: 3 columnas fijas para iPad */
    div.stButton > button { 
        height: 115px !important; 
        border-radius: 12px;
        border: 2px solid #333;
        font-weight: bold !important;
        line-height: 1.2;
    }
    
    /* MEJORA DE HOY: Tiempos mucho más grandes dentro del botón */
    .time-large { font-size: 24px !important; color: #cc0000; font-weight: 800; }
    </style>
    """, unsafe_allow_html=True)

# --- INICIALIZACIÓN (ESTADO FIEL A LA V30.0) ---
if 'players_stats' not in st.session_state:
    # Plantilla de 14 jugadores
    default_players = ["Serra (P)", "Jose (P)", "Julian", "Omar", "Tony", "Rochina", "Benages", "Pedrito", "Parre Jr", "Baeza", "Manu", "Toro", "Silla", "Coque"]
    st.session_state.players_stats = {nom: {'total': 0, 'current_shift': 0, 'last_entry': None, 'in_pista': False} for nom in default_players}
    st.session_state.update({
        'running': False, 'tiempo_acumulado': 0, 'ultimo_click': None, 
        'goles_lud': 0, 'goles_riv': 0, 'show_config': False
    })

s = st.session_state

# --- MEJORA: BOTÓN DE CONFIGURACIÓN DE PLANTILLA ---
if st.button("⚙️ CONFIGURAR NOMBRES"):
    s.show_config = not s.show_config
    st.rerun()

if s.show_config:
    st.subheader("Configuración de la Plantilla (14 Jugadores)")
    st.write("Los 2 primeros nombres se consideran Porteros (Regla 4+1).")
    new_names = []
    cols_cfg = st.columns(3)
    current_names = list(s.players_stats.keys())
    for i in range(14):
        with cols_cfg[i % 3]:
            val = st.text_input(f"Posición {i+1}", value=current_names[i], key=f"cfg_{i}")
            new_names.append(val)
    if st.button("💾 GUARDAR Y VOLVER AL PARTIDO"):
        # Actualiza nombres manteniendo estadísticas si el nombre no cambia
        new_stats = {name: s.players_stats.get(name, {'total': 0, 'current_shift': 0, 'last_entry': None, 'in_pista': False}) for name in new_names}
        s.players_stats = new_stats
        s.show_config = False
        st.rerun()
else:
    # --- LÓGICA DE PARTIDO ORIGINAL (LA QUE FUNCIONA) ---
    if s.running:
        ahora = time.time()
        tiempo_actual = s.tiempo_acumulado + (ahora - s.ultimo_click)
        for p, stats in s.players_stats.items():
            if stats['in_pista']: stats['current_shift'] = ahora - stats['last_entry']
    else:
        tiempo_actual = s.tiempo_acumulado
    
    mins, secs = divmod(int(tiempo_actual), 60)

    # CABECERA ORIGINAL (3 BLOQUES: GOL - CRONO - GOL)
    col_l, col_c, col_r = st.columns([1, 2, 1])
    with col_l:
        st.markdown(f"<div class='score-val'>{s.goles_lud}</div>", unsafe_allow_html=True)
        if st.button("⚽ GOL LUD", use_container_width=True): s.goles_lud += 1; st.rerun()
    with col_c:
        st.markdown(f"<div class='main-clock'>{mins:02d}:{secs:02d}</div>", unsafe_allow_html=True)
        b1, b2 = st.columns(2)
        if b1.button("▶️ START / ⏸️ STOP", use_container_width=True):
            if not s.running:
                s.running = True; s.ultimo_click = time.time()
                for p in s.players_stats.values():
                    if p['in_pista']: p['last_entry'] = s.ultimo_click
            else:
                s.running = False; s.tiempo_acumulado += (time.time() - s.ultimo_click)
                for p in s.players_stats.values():
                    if p['in_pista']: p['total'] += p['current_shift']; p['current_shift'] = 0
            st.rerun()
        if b2.button("🔄 RESET PARTIDO", use_container_width=True):
            s.update({'running': False, 'tiempo_acumulado': 0, 'ultimo_click': None, 'goles_lud': 0, 'goles_riv': 0})
            for p in s.players_stats.values(): p.update({'total': 0, 'current_shift': 0, 'last_entry': None, 'in_pista': False})
            st.rerun()
    with col_r:
        st.markdown(f"<div class='score-val'>{s.goles_riv}</div>", unsafe_allow_html=True)
        if st.button("⚽ GOL RIVAL", use_container_width=True): s.goles_riv += 1; st.rerun()

    st.divider()

    # JUGADORES (3 COLUMNAS ORIGINALES, REGLA 4+1)
    porteros = list(s.players_stats.keys())[:2]
    en_pista_campo = [p for p, stt in s.players_stats.items() if stt['in_pista'] and p not in porteros]
    st.markdown(f"### 🏃 Pista: {len(en_pista_campo)} / 4 de campo")
    
    cols_p = st.columns(3)
    for i, (nom, stats) in enumerate(s.players_stats.items()):
        with cols_p[i % 3]:
            # Tiempos acumulados
            t_total = stats['total'] + (stats['current_shift'] if s.running and stats['in_pista'] else 0)
            m_t, s_t = divmod(int(t_total), 60)
            m_c, s_c = divmod(int(stats['current_shift']), 60)
            
            # ETIQUETA DE BOTÓN: Tiempos destacados y mucho más grandes
            label = f"{nom}\n{m_t:02d}:{s_t:02d} | {m_c:02d}:{s_c:02d}"
            
            if st.button(label, key=f"btn_{nom}", type="primary" if stats['in_pista'] else "secondary"):
                if not stats['in_pista']:
                    if nom in porteros or len(en_pista_campo) < 4:
                        stats['in_pista'] = True
                        stats['last_entry'] = time.time() if s.running else None
                else:
                    stats['in_pista'] = False
                    if s.running and stats['last_entry']:
                        stats['total'] += (time.time() - stats['last_entry'])
                    stats['current_shift'] = 0
                st.rerun()

if s.running:
    time.sleep(1)
    st.rerun()
