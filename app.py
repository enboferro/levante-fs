import streamlit as st
import pandas as pd
import time
from streamlit_autorefresh import st_autorefresh

# 1. CONFIGURACIÓN
st.set_page_config(page_title="LEVANTE UD v2.1", layout="wide")
st_autorefresh(interval=1000, key="f5_refresh")
s = st.session_state

# ESTILOS
st.markdown("""
    <style>
    div.stButton > button { height: 3em; font-weight: bold !important; }
    .main-timer button { height: 5em !important; font-size: 2rem !important; background-color: #003D7A !important; color: white !important; }
    .stop-timer button { height: 5em !important; font-size: 2rem !important; }
    .status-pista { color: #2ecc71; font-weight: bold; }
    .status-banco { color: #e74c3c; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 style='text-align:center;'>Levante UD - Monitorización v2.1</h1>", unsafe_allow_html=True)

# 2. INICIALIZACIÓN
if 'js' not in s:
    n = ["Serra","Julian","Omar","Tony","Rochina","Benages","Pedrito","Parre Jr","Baeza","Manu","Pedro Toro","Paco Silla","Jose","Coque","Nacho Gomez"]
    s.js = [{"n":x,"t":0.0,"i":None,"p":False,"g":0,"s":0,"e":0,"r":0} for x in n]

vars_check = {'ml':0, 'mr':0, 'fl':0, 'fr':0, 'ta':0.0, 'ic':None, 'on':False}
for k, v in vars_check.items():
    if k not in s: s[k] = v

ah = time.time()
transcurrido = s.ta + (ah - s.ic if s.on and s.ic else 0)
tiempo_restante = max(0, 1200 - transcurrido)

# 3. CABECERA Y RESET
c1, c2 = st.columns([4,1])
with c1:
    col_img, col_txt = st.columns([0.5, 3.5])
    col_img.image("https://upload.wikimedia.org/wikipedia/en/thumb/7/7b/Levante_Uni%C3%B3n_Deportiva%2C_S.A.D._logo.svg/200px-Levante_Uni%C3%B3n_Deportiva%2C_S.A.D._logo.svg.png", width=60)
    rv = col_txt.text_input("RIVAL", "RIVAL", label_visibility="collapsed").upper()
if c2.button("🔄 RESET"):
    s.clear()
    st.rerun()

# 4. MARCADOR
m1, m2, m3 = st.columns([2,3,2])
with m1:
    st.metric("LEVANTE UD", s.ml, f"Faltas: {s.fl}")
    if st.button("⚽ GOL LUD", key="btn_g_lud", use_container_width=True): s.ml+=1; st.rerun()
    cf1, cf2 = st.columns(2)
    if cf1.button("F+", key="f_lud_p"): s.fl+=1; st.rerun()
    if cf2.button("F-", key="f_lud_m"): s.fl=max(0, s.fl-1); st.rerun()

with m2:
    mm, sv = divmod(int(tiempo_restante), 60)
    st.markdown(f"<h1 style='text-align:center; font-size:4rem; color:#e74c3c;'>{mm:02d}:{sv:02d}</h1>", unsafe_allow_html=True)
    if not s.on:
        st.markdown('<div class="main-timer">', unsafe_allow_html=True)
        if st.button("▶ START", key="btn_start", use_container_width=True):
            if tiempo_restante > 0:
                s.ic, s.on = ah, True
                for j in s.js: 
                    if j["p"]: j["i"] = ah
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="stop-timer">', unsafe_allow_html=True)
        if st.button("⏸ STOP", key="btn_stop", use_container_width=True):
            s.ta += ah - s.ic
            s.on, s.ic = False, None
            for j in s.js:
                if j["p"] and j["i"]: j["t"] += ah - j["i"]; j["i"] = None
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

with m3:
    st.metric(rv[:6], s.mr, f"Faltas: {s.fr}")
    if st.button(f"⚽ GOL {rv[:3]}", key="btn_g_riv", use_container_width=True): s.mr+=1; st.rerun()
    rf1, rf2 = st.columns(2)
    if rf1.button("F+", key="f_riv_p"): s.fr+=1; st.rerun()
    if rf2.button("F-", key="f_riv_m"): s.fr=max(0, s.fr-1); st.rerun()

# 5. TABLA RESUMEN SUPERIOR (Novedad)
st.divider()
st.subheader("📊 Resumen de Tiempos y Estado")

resumen_data = []
for j in s.js:
    tt_actual = j["t"] + (ah - j["i"] if s.on and j["p"] and j["i"] else 0)
    mj, sj = divmod(int(tt_actual), 60)
    resumen_data.append({
        "Jugador": j["n"],
        "Estado": "PISTA 🟢" if j["p"] else "BANCO 🔴",
        "Tiempo Total": f"{mj:02d}:{sj:02d}",
        "Goles": j["g"]
    })

df_resumen = pd.DataFrame(resumen_data)
st.table(df_resumen) # Tabla estática pero se actualiza cada segundo

# 6. PISTA Y JUGADORES (DETALLE)
st.divider()
en_pista = sum(1 for x in s.js if x["p"])
st.subheader(f"🏃 GESTIÓN DE CAMBIOS ({en_pista} / 5)")

cols = st.columns(3)
for idx, j in enumerate(s.js):
    with cols[idx % 3]:
        with st.container(border=True):
            tt = j["t"] + (ah - j["i"] if s.on and j["p"] and j["i"] else 0)
            mj, sj = divmod(int(tt), 60)
            mins = tt / 60.0
            c_fat = "#2ecc71" if mins <= 3 else ("#f39c12" if mins <= 5 else "#e74c3c")
            
            cn, ct = st.columns([1.5, 1])
            cn.write(f"{'🟢' if j['p'] else '🔴'} **{j['n']}**")
            ct.write(f"⏱️ **{mj:02d}:{sj:02d}**")
            
            ancho = min((mins / 7.0) * 100, 100)
            st.markdown(f'<div style="border:1px solid #ddd;border-radius:5px;background:#eee;height:10px;width:100%;"><div style="background-color:{c_fat};width:{ancho}%;height:100%;border-radius:4px;"></div></div>', unsafe_allow_html=True)
            
            st.write("")
            s1,s2,s3,s4 = st.columns(4)
            if s1.button("🎯", key=f"t{idx}"): j["s"]+=1
            if s2.button("🛡️", key=f"r{idx}"): j["r"]+=1
            if s3.button("❌", key=f"e{idx}"): j["e"]+=1
            if s4.button("⚽", key=f"g{idx}"): j["g"]+=1; s.ml+=1; st.rerun()
            
            bt_txt = "SALIR" if j["p"] else "ENTRAR"
            if st.button(bt_txt, key=f"c{idx}", use_container_width=True):
                if not j["p"] and en_pista < 5:
                    j["p"], j["i"] = True, (ah if s.on else None)
                elif j["p"]:
                    if s.on and j["i"]: j["t"] += ah - j["i"]
                    j["p"], j["i"] = False, None
                st.rerun()

st.divider()
if st.button("💾 DESCARGAR CSV FINAL"):
    st.download_button("BAJAR CSV", pd.DataFrame(s.js).to_csv(index=False).encode('
