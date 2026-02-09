import streamlit as st
import json

# Configuración de la página
st.set_page_config(
    page_title="Hoja de Respuestas ICFES",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Forzar tema oscuro
st.markdown("""
    <script>
        var targetTheme = "dark";
        var currentTheme = window.localStorage.getItem("theme");
        if (currentTheme !== targetTheme) {
            window.localStorage.setItem("theme", targetTheme);
            window.location.reload();
        }
    </script>
""", unsafe_allow_html=True)

# Título
st.title("HOJA DE RESPUESTAS")
st.subheader("PRE-ICFES INTENSIVO")
st.subheader('SMS GROUP')
st.caption("SIMULACRO FINAL DE ENERO 2026")

# Estructura de materias según ICFES real
# (materia, número_preguntas, reinicia_numeración)
ESTRUCTURA_MATERIAS = [
    ('Matemáticas 1', 26, False),
    ('Lectura crítica', 38, False),
    ('Sociales y ciudadanas 1', 26, False),
    ('Ciencias naturales 1', 20, True)  # Reinicia desde 1
]

# Calcular rangos de preguntas para cada materia
def calcular_rangos():
    rangos = {}
    numero_actual = 1
    
    for materia, num_preguntas, reinicia in ESTRUCTURA_MATERIAS:
        if reinicia:
            # Para materias que reinician, siempre empieza desde 1
            rangos[materia] = (1, num_preguntas)
        else:
            # Para materias secuenciales
            rangos[materia] = (numero_actual, numero_actual + num_preguntas - 1)
            numero_actual += num_preguntas
    
    return rangos

RANGOS_PREGUNTAS = calcular_rangos()

# Inicializar el estado de la sesión
if 'respuestas' not in st.session_state:
    st.session_state.respuestas = {materia: {} for materia, _, _ in ESTRUCTURA_MATERIAS}

if 'nombre' not in st.session_state:
    st.session_state.nombre = ""

if 'materia_actual' not in st.session_state:
    st.session_state.materia_actual = "Matemáticas 1"

# Información del estudiante
nombre = st.text_input("NOMBRE:", key="input_nombre", value=st.session_state.nombre)
st.session_state.nombre = nombre

# Opciones de respuesta
opciones = ['A', 'B', 'C', 'D']

# Función para crear botones de respuesta
def crear_botones_pregunta(numero_pregunta, materia):
    # Siempre usa 4 opciones (A, B, C, D)
    cols = st.columns([0.5, 1, 1, 1, 1])
    
    with cols[0]:
        st.write(f"**{numero_pregunta}**")
    
    respuesta_actual = st.session_state.respuestas[materia].get(numero_pregunta, None)
    
    for i, opcion in enumerate(opciones):
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

# Mostrar preguntas de la materia actual
st.divider()
st.header(st.session_state.materia_actual)
st.divider()

inicio, fin = RANGOS_PREGUNTAS[st.session_state.materia_actual]
st.subheader(f"Preguntas {inicio}-{fin}")

for i in range(inicio, fin + 1):
    crear_botones_pregunta(i, st.session_state.materia_actual)

# Sección de controles
st.divider()
col_control1, col_control2, col_control3 = st.columns(3)

with col_control1:
    if st.button("🗑️ Limpiar respuestas de esta materia", use_container_width=True):
        st.session_state.respuestas[st.session_state.materia_actual] = {}
        st.rerun()

with col_control2:
    # Mostrar progreso de la materia actual
    inicio, fin = RANGOS_PREGUNTAS[st.session_state.materia_actual]
    num_preguntas = fin - inicio + 1
    total_respondidas = len(st.session_state.respuestas[st.session_state.materia_actual])
    st.metric(f"Preguntas respondidas", f"{total_respondidas}/{num_preguntas}")

with col_control3:
    # Botón para generar JSON
    if st.button("💾 Generar archivo JSON", type="primary", use_container_width=True):
        # Calcular estadísticas totales
        total_respondidas_global = sum(len(respuestas) for respuestas in st.session_state.respuestas.values())
        
        # Calcular total de preguntas
        total_preguntas_global = sum(num_preg for _, num_preg, _ in ESTRUCTURA_MATERIAS)
        
        # Crear el diccionario con toda la información
        datos_completos = {
            "informacion_estudiante": {
                "nombre": st.session_state.nombre
            },
            "respuestas": st.session_state.respuestas,
            "estadisticas": {
                "total_preguntas": total_preguntas_global,
                "preguntas_respondidas": total_respondidas_global,
                "preguntas_sin_responder": total_preguntas_global - total_respondidas_global,
                "por_materia": {
                    materia: {
                        "rango": f"{RANGOS_PREGUNTAS[materia][0]}-{RANGOS_PREGUNTAS[materia][1]}",
                        "respondidas": len(respuestas),
                        "sin_responder": (RANGOS_PREGUNTAS[materia][1] - RANGOS_PREGUNTAS[materia][0] + 1) - len(respuestas)
                    }
                    for materia, respuestas in st.session_state.respuestas.items()
                }
            }
        }
        
        # Convertir a JSON
        json_data = json.dumps(datos_completos, indent=4, ensure_ascii=False)
        
        # Crear nombre de archivo
        nombre_estudiante = st.session_state.nombre if st.session_state.nombre else "estudiante"
        nombre_archivo = f"respuestas_{nombre_estudiante}.json"
        
        # Botón de descarga
        st.download_button(
            label="⬇️ Descargar JSON",
            data=json_data,
            file_name=nombre_archivo,
            mime="application/json",
            use_container_width=True
        )
        
        st.success("✅ Archivo JSON generado correctamente")

# Mostrar resumen de respuestas de la materia actual
if st.session_state.respuestas[st.session_state.materia_actual]:
    st.divider()
    st.subheader(f"📊 Resumen de Respuestas - {st.session_state.materia_actual}")
    
    resumen_cols = st.columns(4)
    
    # Crear un resumen visual
    for i, opcion in enumerate(opciones):
        with resumen_cols[i]:
            count = list(st.session_state.respuestas[st.session_state.materia_actual].values()).count(opcion)
            st.metric(f"Opción {opcion}", count)

# Sidebar con selección de materias
with st.sidebar:
    st.header("📚 MATERIAS")
    st.divider()
    
    # Crear botones para cada materia
    for materia, num_preguntas, _ in ESTRUCTURA_MATERIAS:
        respondidas = len(st.session_state.respuestas[materia])
        emoji = "✅" if respondidas == num_preguntas else "📝"
        
        # Determinar el tipo de botón
        tipo = "primary" if st.session_state.materia_actual == materia else "secondary"
        
        inicio, fin = RANGOS_PREGUNTAS[materia]
        label = f"{emoji} {materia} ({respondidas}/{num_preguntas})"
        
        if st.button(
            label,
            key=f"materia_{materia}",
            type=tipo,
            use_container_width=True
        ):
            st.session_state.materia_actual = materia
            st.rerun()
    
    st.divider()
    
    # Resumen global
    st.subheader("📊 Progreso Total")
    total_global = sum(len(respuestas) for respuestas in st.session_state.respuestas.values())
    total_preguntas = sum(num_preg for _, num_preg, _ in ESTRUCTURA_MATERIAS)
    st.progress(total_global / total_preguntas)
    st.metric("Total respondidas", f"{total_global}/{total_preguntas}")
    
    st.divider()
    
    # Información de rangos
    st.subheader("📋 Rangos de Preguntas")
    for materia, _, _ in ESTRUCTURA_MATERIAS:
        inicio, fin = RANGOS_PREGUNTAS[materia]
        st.caption(f"**{materia}:** {inicio}-{fin}")
    
    st.divider()
    
    # Botón para limpiar todo
    if st.button("🗑️ Limpiar todo", use_container_width=True):
        st.session_state.respuestas = {materia: {} for materia, _, _ in ESTRUCTURA_MATERIAS}
        st.rerun()
