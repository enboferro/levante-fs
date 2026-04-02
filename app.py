import streamlit as st
import pandas as pd
import time
import io
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="LUD v3.2 - Gestión de Partes", layout="wide")
s = st.session_state

# 1. INICIALIZACIÓN
if 'js' not in s:
    n = ["Serra","Julian","Omar","Tony","Rochina","Benages","Pedrito","Parre Jr","Baeza","Manu","Pedro Toro","Paco Silla","Jose","Coque","Nacho Gomez"]
    # t = tiempo en la parte actual, t_1t = tiempo guardado de la primera parte
    s.js = [{"n":x,"t":0.0,"t_1t":0.0,"i":None,"p":False,"g":0,"s":0,"e":0,"r":0} for x in n]
    s.ml, s.mr, s.fl, s.fr = 0, 0, 0, 0
    s.ta, s.ic, s.on = 0.0, None, False
    s.parte = "1T"
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
    if s.ta == 0 and not s.on and s.parte == "1T":
        iniciales = st.multiselect("Quinteto Inicial", [j["n"] for j in s.js], max_selections=5)
        if st.button("Confirmar"):
            for j in s.js: j["p"] = True if j["n"] in iniciales else False
            st.rerun()

if c3.button("🔄 RESET"):
    s.clear(); st.rerun()

t1, t2, t3 = st.tabs(["⏱️ PANEL PARTIDO", "📊 ACUMULADO TOTAL", "💾 FINALIZAR"])

with t1:
    st.subheader(f"CRONÓMETRO {s.parte}")
    m1, m2, m3 = st.columns([2,3,2])
    
    with m1:
        st.metric("LUD", s.ml, f"Faltas: {s.fl}")
        if st.button("⚽ GOL LUD", use_container_width=1): s.ml+=1; st.rerun()
        f1, f2 = st.columns(2)
        if f1.button("F+", key="flp"): s.fl+=1; st.rerun()
        if f2.button("F-", key="flm"): s.fl=max(0, s.fl-1); st.rerun()
        
    with m2:
        mm, sv = divmod(int(rem), 60)
        st.markdown(f"<h1 style='text-align:center;font-size:5rem;color:red;'>{mm:02d}:{sv:02d}</h1>", 1)
        if not s.on:
            if st.button("▶ START", use_container_width=1, type="primary"):
                if rem > 0:
                    s.ic, s.on = ah, True
                    for j in s.js: 
                        if j["p"]: j["i"] = ah
                    st.rerun()
        else:
            if st.button("⏸ STOP", use_container_width=1, type="secondary"):
                s.ta += ah - s.ic
                s.on, s.ic = False, None
                for j in s.js:
                    if j["p"] and j["i"]: 
                        j["t"] += ah - j["i"]
                        j["i"] = None
                st.rerun()

    with m3:
        st.metric(rv[:6], s.mr, f"Faltas: {s.fr}")
        if st.button(f"⚽ GOL {rv[:3]}", use_container_width=1): s.mr+=1; st.rerun()
        r1, r2 = st.columns(2)
        if r1.button("F+", key="frp"): s.fr+=1; st.rerun()
        if r2.button("F-", key="frm"): s.fr=max(0, s.fr-1); st.rerun()

    st.divider()
    ep = sum(1 for x in s.js if x["p"])
    cols = st.columns(4)
    for idx, j in enumerate(s.js):
        with cols[idx % 4]:
            with st.container(border=True):
                # TIEMPO SOLO DE LA PARTE ACTUAL
                t_parte = j["t"] + (ah - j["i"] if s.on and j["p"] and j["i"] else 0)
                m_j,v_j = divmod(int(t_parte), 60)
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
    st.subheader("📊 TIEMPO TOTAL ACUMULADO (1T + 2T)")
    m_cols = st.columns(5)
    for idx, j in enumerate(s.js):
        # Sumamos tiempo 1T + tiempo actual del 2T
        t_total = j["t_1t"] + j["t"] + (ah - j["i"] if s.on and j["p"] and j["i"] else 0)
        m_j,v_j = divmod(int(t_total), 60)
        m_cols[idx % 5].write(f"**{j['n']}**: {m_j:02d}:{v_j:02d}")

with t3:
    if s.parte == "1T":
        if st.button("🏁 FINALIZAR 1T Y REINICIAR FALTAS", type="primary", use_container_width=True):
            if s.on: # Si estaba en marcha, guardamos tiempo actual
                s.ta += ah - s.ic
                for j in s.js:
                    if j["p"] and j["i"]: j["t"] += ah - j["i"]
            
            # Transferimos tiempo del 1T a la memoria histórica y reseteamos el contador de "parte"
            for j in s.js:
                j["t_1t"] = j["t"]
                j["t"] = 0.0
                j["i"] = None
            
            # Reset Reloj y Faltas (Marcador NO se toca)
            s.fl, s.fr = 0, 0
            s.ta, s.ic, s.on = 0.0, None, False
            s.parte = "2T"
            st.rerun()
    else:
        st.success("SEGUNDA PARTE EN CURSO")

    st.divider()
    if st.button("💾 GENERAR EXCEL"):
        s.exp = True
        datos = []
        for j in s.js:
            t_final = j["t_1t"] + j["t"] + (ah - j["i"] if s.on and j["p"] and j["i"] else 0)
            m_e, v_e = divmod(int(t_final), 60)
            datos.append({"Jugador": j["n"], "Tiempo Total": f"{m_e:02d}:{v_e:02d}", "Goles": j["g"], "Tiros": j["s"], "Robos": j["r"], "Pérdidas": j["e"]})
        
        df = pd.DataFrame(datos)
        out = io.BytesIO()
        with pd.ExcelWriter(out, engine='openpyxl') as w:
            df.to_excel(w, index=False)
        st.download_button("📥 DESCARGAR EXCEL", out.getvalue(), f"Informe_{rv}.xlsx")
        if st.button("Reanudar"): s.exp = False; st.rerun()
