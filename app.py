import streamlit as st

# 1. Configuración de la página (opcional)
st.set_page_config(page_title="Mi App de Registro", layout="wide")

# 2. Inicialización del Session State
# Es vital inicializar 'fr' para que no dé error al cargar la app
if 'fr' not in st.session_state:
    st.session_state.fr = 0

# Alias para acortar el código como lo tienes en tu error
ss = st.session_state

st.title("Panel de Control")

# 3. Creación de columnas (basado en tu variable 'c4')
c1, c2, c3, c4 = st.columns(4)

# --- SECCIÓN DE LA LÍNEA 87 ---

with c1:
    st.write("Columna 1")
    # Otros elementos...

with c2:
    st.write("Columna 2")

with c3:
    st.write("Columna 3")

# Aquí es donde estaba el problema:
# Añadimos 'key' para que el ID sea constante aunque el texto cambie
if c4.button(f"⚠️ FALTA ({ss.fr})", use_container_width=True, key="boton_contador_falta"): 
    ss.fr += 1
    st.rerun()

# ------------------------------

# 4. Mostrar el resultado actual
st.divider()
st.info(f"El contador actual es: {ss.fr}")
