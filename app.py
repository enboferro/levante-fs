import streamlit as st
import time

# Configuración de página para iPad 10"
st.set_page_config(page_title="LUD FUTSAL - Configurable", layout="wide")

st.markdown("""
    <style>
    .block-container { padding: 1rem 2rem; }
    .main-clock { 
        font-size: 150px !important; font-weight: 900; text-align: center; 
        line-height: 1; color: #1d1d1d; font-family: monospace; 
    }
    .score-val { font-size: 100px; font-weight: 900; text-align: center; line-height: 1; }
    div.stButton > button { height: 90px !important; font-size: 20px !important; font-weight: bold !important; border-radius: 12px; }
    </style>
    """, unsafe_allow_html=True)

# --- INICIALIZACIÓN ---
if 'players_stats' not in st.session_state:
    # Plantilla inicial por defecto
    default_players = ["Serra", "Julian", "Omar", "Tony", "Rochina", "Benages", "Pedrito", "Parre Jr", "Baeza", "Manu", "Toro", "Silla", "Jose", "Coque", "Nacho"]
    st.session_state.players_stats = {nom: {'total': 0, 'current_shift': 0, 'last_entry': None, 'in_pista': False} for nom in default_players}
    st.session_state.update({
        'running': False, 'tiempo_acumulado': 0, 'ultimo_click': None, 
        'goles_lud': 0, 'goles_riv': 0, 'mode': 'Partido'
    })

s = st.session_state

# --- BARRA SUPERIOR DE MODO ---
s.mode = st.radio("SELECCIONAR MODO:", ["Partido", "Configurar Plantilla"], horizontal=True)

st.divider()

# --- MODO CONFIGURACIÓN ---
if s.mode == "Configurar Plantilla":
    st.subheader("⚙️ Configuración de los 15 Jugadores")
    st.info("Cambia los nombres aquí y aparecerán automáticamente en los botones de partido.")
    
    current_names = list(s.players_stats.keys())
    new_names = []
    
    cols = st.columns(3)
    for i in range(15):
        with cols[i % 3]:
            name = st.text_input(f"Jugador {i+1}", value=current_names[i] if i < len(current_names) else f"Jugador {i+1}")
            new_names.append(name)
    
    if st.button("💾 GUARDAR Y ACTUALIZAR PLANTILLA"):
        # Solo actualizamos si cambian los nombres para no resetear stats en mitad de un partido por error
        new_stats = {}
        for name in new_names:
            if name in s.players_stats:
                new_stats[name] = s.players_stats[name]
            else:
                new_stats[name] = {'total': 0, 'current_shift': 0, 'last_entry': None, 'in_pista': False}
        s.players_stats = new_stats
        st.success("Plantilla actualizada correctamente.")
        st.rerun()

# --- MODO PARTIDO ---
else:
    # Lógica de tiempo
    if s.running:
        ahora = time.time()
        tiempo_actual = s.tiempo_acumulado + (ahora - s.ultimo_click)
        for p, stats in s.players_stats.items():
            if stats['in_pista']: stats['current_shift'] = ahora - stats['last_entry']
    else:
        tiempo_actual = s.tiempo_acumulado
    
    mins, secs = divmod(int(tiempo_actual), 60)

    # Marcador y Cronómetro
    col_l, col_c, col_r = st.columns([1, 2, 1])
    with col_l:
        st.markdown(f"<div class='score-val'>{s.goles_lud}</div>", unsafe_allow_html=True)
        if st.button("⚽ GOL LUD"): s.goles_lud += 1; st.rerun()
    with col_c:
        st.markdown(f"<div class='main-clock'>{mins:02d}:{secs:02d}</div>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        if c1.button("▶️ / ⏸️", use_container_width=True):
            if not s.running:
                s.running = True; s.ultimo_click = time.time()
                for p in s.players_stats.values():
                    if p['in_pista']: p['last_entry'] = s.ultimo_click
            else:
                s.running = False; s.tiempo_acumulado += (time.time() - s.ultimo_click)
                for p in s.players_stats.values():
                    if p['in_pista']: p['total'] += p['current_shift']; p['current_shift'] = 0
            st.rerun()
        if c2.button("🔄 RESET", use_container_width=True):
            # Reset total de partido
            for p in s.players_stats.values():
                p.update({'total': 0, 'current_shift': 0, 'last_entry': None, 'in_pista': False})
            s.update({'running': False, 'tiempo_acumulado': 0, 'ultimo_click': None, 'goles_lud': 0, 'goles_riv': 0})
            st.rerun()
    with col_r:
        st.markdown(f"<div class='score-val'>{s.goles_riv}</div>", unsafe_allow_html=True)
        if st.button("⚽ GOL RIV"): s.goles_riv += 1; st.rerun()

    st.write("")
    
    # Jugadores
    p_campo = [p for p, stt in s.players_stats.items() if stt['in_pista'] and p not in ["Serra", "Jose"]]
    st.markdown(f"### 🏃 Pista: {len(p_campo)} / 4")
    
    cols = st.columns(3)
    for i, (nom, stats) in enumerate(s.players_stats.items()):
        with cols[i % 3]:
            t_total = stats['total'] + (stats['current_shift'] if s.running and stats['in_pista'] else 0)
            m_t, s_t = divmod(int(t_total), 60)
            m_c, s_c = divmod(int(stats['current_shift']), 60)
            
            label = f"{nom}\n{m_t:02d}:{s_t:02d} | {m_c:02d}:{s_c:02d}"
            
            if st.button(label, key=f"btn_{nom}", type="primary" if stats['in_pista'] else "secondary"):
                if not stats['in_pista']:
                    if nom in ["Serra", "Jose"] or len(p_campo) < 4:
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
