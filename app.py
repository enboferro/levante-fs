# 3. MARCADOR Y RELOJ CENTRAL
with st.container():
    m_col1, m_col2, m_col3 = st.columns([2, 2, 2])
    
    with m_col1:
        # Añadido color:white en el h2
        st.markdown(f"<div style='text-align:center; background:#003D7A; color:white; padding:10px; border-radius:10px;'><h2 style='color:white !important;'>LUD: {ss.ml}</h2></div>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        if c1.button("⚽ GOL LUD", use_container_width=True): ss.ml+=1; st.rerun()
        if c2.button(f"⚠️ FALTA ({ss.fl})", use_container_width=True, key="btn_falta_lud"): ss.fl+=1; st.rerun()

    with m_col2:
        # RELOJ EFECTIVO (Sin cambios, ya que el fondo es blanco)
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
        # Añadido color:white en el h2
        st.markdown(f"<div style='text-align:center; background:#7A0019; color:white; padding:10px; border-radius:10px;'><h2 style='color:white !important;'>RIVAL: {ss.mr}</h2></div>", unsafe_allow_html=True)
        c3, c4 = st.columns(2)
        if c3.button("⚽ GOL RIV", use_container_width=True): ss.mr+=1; st.rerun()
        if c4.button(f"⚠️ FALTA ({ss.fr})", use_container_width=True, key="btn_falta_riv"): ss.fr+=1; st.rerun()

