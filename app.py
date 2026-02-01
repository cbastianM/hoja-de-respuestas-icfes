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

# Inicializar el estado de la sesión
if 'respuestas' not in st.session_state:
    st.session_state.respuestas = {
        'Lectura': {},
        'Matemáticas': {},
        'Naturales': {},
        'Sociales': {},
        'Inglés': {}
    }

if 'nombre' not in st.session_state:
    st.session_state.nombre = ""

if 'materia_actual' not in st.session_state:
    st.session_state.materia_actual = "Lectura"

# Información del estudiante
nombre = st.text_input("NOMBRE:", key="input_nombre", value=st.session_state.nombre)
st.session_state.nombre = nombre

# Opciones de respuesta
opciones = ['A', 'B', 'C', 'D']

# Función para crear botones de respuesta
def crear_botones_pregunta(numero_pregunta, materia):
    # Determinar opciones según la materia y número de pregunta
    if materia == "Inglés" and 7 <= numero_pregunta <= 12:
        opciones_pregunta = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
        cols = st.columns([1, 1, 1, 1, 1, 1, 1, 1, 1])
    else:
        opciones_pregunta = opciones
        cols = st.columns([1, 2, 2, 2, 2])
    
    with cols[0]:
        st.write(f"**{numero_pregunta}**")
    
    respuesta_actual = st.session_state.respuestas[materia].get(numero_pregunta, None)
    
    inicio_opciones = 0 if len(opciones_pregunta) == 8 else 1
    
    for i, opcion in enumerate(opciones_pregunta):
        with cols[i + inicio_opciones]:
            # Determinar el tipo de botón según si está seleccionado
            tipo_boton = "primary" if respuesta_actual == opcion else "secondary"
            
            if st.button(
                opcion,
                key=f"q{numero_pregunta}_{opcion}_{materia}",
                type=tipo_boton,
                use_container_width=True
            ):
                st.session_state.respuestas[materia][numero_pregunta] = opcion
                st.rerun()

# Crear una sola columna para todas las preguntas (1-40)
st.divider()
st.header(st.session_state.materia_actual)
st.divider()

st.subheader("Preguntas 1-40")
for i in range(1, 41):
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
    total_respondidas = len(st.session_state.respuestas[st.session_state.materia_actual])
    st.metric(f"Preguntas respondidas ({st.session_state.materia_actual})", f"{total_respondidas}/40")

with col_control3:
    # Botón para generar JSON
    if st.button("💾 Generar archivo JSON", type="primary", use_container_width=True):
        # Calcular estadísticas totales
        total_respondidas_global = sum(len(respuestas) for respuestas in st.session_state.respuestas.values())
        total_preguntas_global = 200  # 5 materias x 40 preguntas
        
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
                        "respondidas": len(respuestas),
                        "sin_responder": 40 - len(respuestas)
                    }
                    for materia, respuestas in st.session_state.respuestas.items()
                }
            }
        }
        
        # Convertir a JSON
        json_data = json.dumps(datos_completos, indent=4, ensure_ascii=False)
        
        # Crear nombre de archivo
        nombre_estudiante = st.session_state.nombre if st.session_state.nombre else "estudiante"
        nombre_archivo = f"respuestas de {nombre_estudiante}.json"
        
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
    
    # Determinar opciones según la materia
    if st.session_state.materia_actual == "Inglés":
        # Contar respuestas de preguntas 7-12 (A-H) y el resto (A-D)
        opciones_resumen = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
        resumen_cols = st.columns(8)
    else:
        opciones_resumen = opciones
        resumen_cols = st.columns(4)
    
    # Crear un resumen visual
    for i, opcion in enumerate(opciones_resumen):
        with resumen_cols[i]:
            count = list(st.session_state.respuestas[st.session_state.materia_actual].values()).count(opcion)
            st.metric(f"Opción {opcion}", count)

# Sidebar con selección de materias
with st.sidebar:
    st.header("📚 MATERIAS")
    st.divider()
    
    # Crear botones para cada materia
    materias = ['Lectura', 'Matemáticas', 'Naturales', 'Sociales', 'Inglés']
    
    for materia in materias:
        respondidas = len(st.session_state.respuestas[materia])
        emoji = "✅" if respondidas == 40 else "📝"
        
        # Determinar el tipo de botón
        tipo = "primary" if st.session_state.materia_actual == materia else "secondary"
        
        if st.button(
            f"{emoji} {materia} ({respondidas}/40)",
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
    st.progress(total_global / 200)
    st.metric("Total respondidas", f"{total_global}/200")
    
    st.divider()
    
    # Botón para limpiar todo
    if st.button("🗑️ Limpiar todo", use_container_width=True):
        st.session_state.respuestas = {
            'Lectura': {},
            'Matemáticas': {},
            'Naturales': {},
            'Sociales': {},
            'Inglés': {}
        }
        st.rerun()
