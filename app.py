import streamlit as st
import json

# Configuración de la página
st.set_page_config(
    page_title="Hoja de Respuestas ICFES",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Título
st.title("HOJA DE RESPUESTAS")
st.subheader("PRE-ICFES INTENSIVO")
st.subheader('SMS GROUP')
st.caption("SIMULACRO FEBRERO 2026")

# ============================================================
# CONFIGURACIÓN DE MATERIAS - EDITA AQUÍ FÁCILMENTE
# ============================================================
# Formato: (nombre_materia, pregunta_inicio, pregunta_fin, opciones)
# - opciones: lista de opciones de respuesta para esa materia

OPCIONES_ABCD = ['A', 'B', 'C', 'D']
OPCIONES_INGLES = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']

MATERIAS_CONFIG = [
    ('Matemáticas',           1, 40, OPCIONES_ABCD),
    ('Lectura crítica',       1, 40, OPCIONES_ABCD),
    ('Sociales y ciudadanas', 1, 40, OPCIONES_ABCD),
    ('Ciencias naturales',    1, 40, OPCIONES_ABCD),
    ('Inglés',                1, 40, OPCIONES_INGLES),
]
# ============================================================

# Inicializar estado
if 'respuestas' not in st.session_state:
    st.session_state.respuestas = {m: {} for m, _, _, _ in MATERIAS_CONFIG}

if 'nombre' not in st.session_state:
    st.session_state.nombre = ""

if 'materia_actual' not in st.session_state:
    st.session_state.materia_actual = MATERIAS_CONFIG[0][0]

# Validar que materia_actual existe en config actual
if st.session_state.materia_actual not in [m for m, _, _, _ in MATERIAS_CONFIG]:
    st.session_state.materia_actual = MATERIAS_CONFIG[0][0]

# Sincronizar respuestas con config (por si se cambian materias)
for materia, _, _, _ in MATERIAS_CONFIG:
    if materia not in st.session_state.respuestas:
        st.session_state.respuestas[materia] = {}

# Info del estudiante
nombre = st.text_input("NOMBRE:", key="input_nombre", value=st.session_state.nombre)
st.session_state.nombre = nombre


def crear_botones_pregunta(numero_pregunta, materia, opciones_materia):
    num_opciones = len(opciones_materia)
    # Columna para número + columnas para cada opción
    col_widths = [0.5] + [1] * num_opciones
    cols = st.columns(col_widths)
    
    with cols[0]:
        st.write(f"**{numero_pregunta}**")
    
    respuesta_actual = st.session_state.respuestas[materia].get(numero_pregunta, None)
    
    for i, opcion in enumerate(opciones_materia):
        with cols[i + 1]:
            tipo_boton = "primary" if respuesta_actual == opcion else "secondary"
            if st.button(
                opcion,
                key=f"q{numero_pregunta}_{opcion}_{materia}",
                type=tipo_boton,
                use_container_width=True
            ):
                st.session_state.respuestas[materia][numero_pregunta] = opcion
                st.rerun()

# Obtener datos de materia actual
materia_actual = st.session_state.materia_actual
inicio, fin, opciones_actuales = next((i, f, o) for m, i, f, o in MATERIAS_CONFIG if m == materia_actual)
num_preguntas = fin - inicio + 1

# Mostrar preguntas
st.divider()
st.header(materia_actual)
st.subheader(f"Preguntas {inicio}-{fin}")
st.divider()

for i in range(inicio, fin + 1):
    crear_botones_pregunta(i, materia_actual, opciones_actuales)

# Controles
st.divider()
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🗑️ Limpiar respuestas de esta materia", use_container_width=True):
        st.session_state.respuestas[materia_actual] = {}
        st.rerun()

with col2:
    total_respondidas = len(st.session_state.respuestas[materia_actual])
    st.metric("Preguntas respondidas", f"{total_respondidas}/{num_preguntas}")

with col3:
    if st.button("💾 Generar archivo JSON", type="primary", use_container_width=True):
        total_respondidas_global = sum(len(r) for r in st.session_state.respuestas.values())
        total_preguntas_global = sum(f - i + 1 for _, i, f, _ in MATERIAS_CONFIG)
        
        datos_completos = {
            "informacion_estudiante": {"nombre": st.session_state.nombre},
            "respuestas": st.session_state.respuestas,
            "estadisticas": {
                "total_preguntas": total_preguntas_global,
                "preguntas_respondidas": total_respondidas_global,
                "preguntas_sin_responder": total_preguntas_global - total_respondidas_global,
                "por_materia": {
                    m: {
                        "rango": f"{i}-{f}",
                        "respondidas": len(st.session_state.respuestas.get(m, {})),
                        "sin_responder": (f - i + 1) - len(st.session_state.respuestas.get(m, {}))
                    }
                    for m, i, f, _ in MATERIAS_CONFIG
                }
            }
        }
        
        json_data = json.dumps(datos_completos, indent=4, ensure_ascii=False)
        nombre_archivo = f"respuestas_{st.session_state.nombre or 'estudiante'}.json"
        
        st.download_button(
            label="⬇️ Descargar JSON",
            data=json_data,
            file_name=nombre_archivo,
            mime="application/json",
            use_container_width=True
        )
        st.success("✅ Archivo JSON generado correctamente")

# Resumen de respuestas
if st.session_state.respuestas[materia_actual]:
    st.divider()
    st.subheader(f"📊 Resumen - {materia_actual}")
    resumen_cols = st.columns(len(opciones_actuales))
    for i, opcion in enumerate(opciones_actuales):
        with resumen_cols[i]:
            count = list(st.session_state.respuestas[materia_actual].values()).count(opcion)
            st.metric(f"Opción {opcion}", count)

# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    st.header("📚 MATERIAS")
    st.divider()
    
    for materia, ini, fi, _ in MATERIAS_CONFIG:
        n_preg = fi - ini + 1
        respondidas = len(st.session_state.respuestas.get(materia, {}))
        emoji = "✅" if respondidas == n_preg else "📝"
        tipo = "primary" if materia_actual == materia else "secondary"
        
        if st.button(
            f"{emoji} {materia} ({respondidas}/{n_preg})",
            key=f"materia_{materia}",
            type=tipo,
            use_container_width=True
        ):
            st.session_state.materia_actual = materia
            st.rerun()
    
    st.divider()
    
    # Progreso total
    st.subheader("📊 Progreso Total")
    total_global = sum(len(r) for r in st.session_state.respuestas.values())
    total_preguntas = sum(f - i + 1 for _, i, f, _ in MATERIAS_CONFIG)
    st.progress(total_global / total_preguntas if total_preguntas > 0 else 0)
    st.metric("Total respondidas", f"{total_global}/{total_preguntas}")
    
    st.divider()
    
    # Tabla de rangos
    st.subheader("📋 Rangos de Preguntas")
    for materia, ini, fi, opts in MATERIAS_CONFIG:
        opciones_str = f" (Opciones: {opts[0]}-{opts[-1]})" if len(opts) > 4 else ""
        st.caption(f"**{materia}:** {ini}-{fi}{opciones_str}")
    
    st.divider()
    
    if st.button("🗑️ Limpiar todo", use_container_width=True):
        st.session_state.respuestas = {m: {} for m, _, _, _ in MATERIAS_CONFIG}
        st.rerun()
