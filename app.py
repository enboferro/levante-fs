import streamlit as st
import pandas as pd
import time
import io
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="LUD v3.0 - Profesional", layout="wide")
s = st.session_state

# 1. INICIALIZACIÓN COMPLETA
if 'js' not in s:
    n = ["Serra","Julian","Omar","Tony","Rochina","Benages","Pedrito","Parre Jr","Baeza","Manu","Pedro Toro","Paco Silla","Jose","Coque","Nacho Gomez"]
    s.js = [{"n":x,"t":0.0,"i":None,"p":False,"g":0,"s":0,"e":0,"r":0} for x in n]
    s.ml, s.mr, s.fl, s.fr = 0, 0, 0, 0
    s.ta, s.ic, s.on = 0.0, None, False
    s.parte = "1T"
    s.historial = {"1T": {"ml":0, "mr":0, "fl":0, "fr":0}, "2T": {"ml":0, "mr":0, "fl":0, "fr":0}}
    s.exp = False

if not s.exp:
    st_autorefresh(interval=1000, key="f5")

ah = time.time()
tr = s.ta + (ah - s.ic if s.on and s.ic else 0)
rem = max(0, 1200 - tr)

# --- CABECERA ---
c1, c2, c3 = st.columns([3,2,1])
with c1:
    col_i, col_t = st.columns([0.5, 3.5])
    col_i.image("https://upload.wikimedia.org/wikipedia/en/thumb/7/7b/Levante_Uni%C3%B3n_Deportiva%2C_S.A.D._logo.svg/200px-Levante_Uni%C3%B3n_Deportiva%2C_S.A.D._logo.svg.png", width=50)
    rv = col_t.text_input("RIVAL", "RIVAL", label_visibility="collapsed").upper()

with c2:
    # SELECCIÓN QUINTETO INICIAL (Solo si no ha empezado el tiempo)
    if s.ta == 0 and not s.on:
        iniciales = st.multiselect("Selecciona Quinteto Inicial", [j["n"] for j in s.js], max_selections=5)
        if st.button("Confirmar Quinteto"):
            for j in s.js:
                j["p"] = True if j["n"] in iniciales else False
            st.rerun()

if c3.button("🔄 RESET TODO"):
    s.clear(); st.rerun()

# --- PESTAÑAS ---
t1, t2, t3 = st.tabs(["⏱️ PARTIDO", "📊 MONITOR ACUMULADO", "💾 FINALIZAR / EXCEL"])

with t1:
    st.subheader(f"MODO: {s.parte}")
    m1, m2, m3 = st.columns([2,3,2])
    
    with m1:
        st.metric(f"LUD ({s.parte})", s.ml, f"Faltas: {s.fl}")
        if st.button("⚽ GOL LUD", use_container_width=1): s.ml+=1; st.rerun()
        f1, f2 = st.columns(2)
        if f1.button("F+", key="flp"): s.fl+=1; st.rerun()
        if f2.button("F-", key="flm"): s.fl=max(0, s.fl-1); st.rerun()
        
    with m2:
        mm, sv = divmod(int(rem), 60)
        st.markdown(f"<h1 style='text-align:center;font-size:5rem;color:red;'>{mm:02d}:{sv:02d}</h1>", 1)
        if not s.on:
            if st.button("▶ START TIEMPO", use_container_width=1, type="primary"):
                s.ic, s.on, s.exp = ah, True, False
                for j in s.js: 
                    if j["p"]: j["i"] = ah
                st.rerun()
        else:
            if st.button("⏸ STOP TIEMPO", use_container_width=1, type="secondary"):
                s.ta += ah - s.ic
                s.on, s.ic = False, None
                for j in s.js:
                    if j["p"] and j["i"]: j["t"]+=ah-j["i"]; j["i"]=None
                st.rerun()

    with m3:
        st.metric(f"{rv[:6]} ({s.parte})", s.mr, f"Faltas: {s.fr}")
        if st.button(f"⚽ GOL {rv[:3]}", use_container_width=1): s.mr+=1; st.rerun()
        r1, r2 = st.columns(2)
        if r1.button("F+", key="frp"): s.fr+=1; st.rerun()
        if r2.button("F-", key="frm"): s.fr=max(0, s.fr-1); st.rerun()

    st.divider()
    # JUGADORES (4 COLUMNAS)
    ep = sum(1 for x in s.js if x["p"])
    cols = st.columns(4)
    for idx, j in enumerate(s.js):
        with cols[idx % 4]:
            with st.container(border=True):
                cur = j["t"]+(ah-j["i"] if s.on and j["p"] and j["i"] else 0)
                m_j,v_j = divmod(int(cur), 60)
                st.write(f"{'🟢' if j['p'] else '🔴'} **{j['n']}** | {m_j:02d}:{v_j:02d}")
                s1,s2,s3,s4 = st.columns(4)
                if s1.button("🎯", key=f"t{idx}"): j["s"]+=1
                if s2.button("🛡️", key=f"r{idx}"): j["r"]+=1
                if s3.button("❌", key=f"e{idx}"): j["e"]+=1
                if s4.button("⚽", key=f"g{idx}"): j["g"]+=1; s.ml+=1; st.rerun()
                if st.button("CAMBIO", key=f"c{idx}", use_container_width=1):
                    if not j["p"] and ep < 5:
                        j["p"], j["i"] = True, (ah if s.on else None)
                    elif j["p"]:
                        if s.on and j["i"]: j["t"] += ah - j["i"]
                        j["p"], j["i"] = False, None
                    st.rerun()

with t2:
    st.subheader("📊 Resumen de Tiempos Acumulados")
    m_cols = st.columns(5)
    for idx, j in enumerate(s.js):
        cur = j["t"]+(ah-j["i"] if s.on and j["p"] and j["i"] else 0)
        m_j,v_j = divmod(int(cur), 60)
        m_cols[idx % 5].write(f"**{j['n']}**: {m_j:02d}:{v_j:02d}")

with t3:
    st.subheader("⚙️ Gestión de Partes y Exportación")
    
    if s.parte == "1T":
        if st.button("🏁 FINALIZAR 1T Y PASAR AL 2T", type="primary"):
            # Guardar datos 1T
            s.historial["1T"] = {"ml": s.ml, "mr": s.mr, "fl": s.fl, "fr": s.fr}
            # Reset marcador y faltas para el 2T
            s.ml, s.mr, s.fl, s.fr = 0, 0, 0, 0
            s.ta, s.ic, s.on = 0.0, None, False
            s.parte = "2T"
            for j in s.js: j["i"] = None # Reset timestamps individuales
            st.rerun()
    else:
        st.info("Actualmente en la SEGUNDA PARTE. Los datos del 1T están guardados.")

    st.divider()
    if st.button("💾 GENERAR EXCEL FINAL DEL PARTIDO"):
        s.exp = True
        datos_excel = []
        for j in s.js:
            total_s = j["t"] + (ah - j["i"] if s.on and j["p"] and j["i"] else 0)
            m_e, v_e = divmod(int(total_s), 60)
            datos_excel.append({
                "Jugador": j["n"], "Tiempo": f"{m_e:02d}:{v_e:02d}",
                "Goles": j["g"], "Tiros": j["s"], "Robos": j["r"], "Pérdidas": j["e"]
            })
        
        df = pd.DataFrame(datos_excel)
        # Añadir resumen de goles totales al final del df si se desea
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Estadisticas')
        
        st.success("Informe consolidado listo.")
        st.download_button("📥 DESCARGAR EXCEL", output.getvalue(), f"Partido_Completo_{rv}.xlsx")
        
        if st.button("🔄 REANUDAR APP"):
            s.exp = False; st.rerun()

st.write(f"v3.0 | Parte: {s.parte} | Marcador Global: {s.historial['1T']['ml'] + s.ml} - {s.historial['1T']['mr'] + s.mr}")
