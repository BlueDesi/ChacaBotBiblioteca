# app.py - Versión final con respuesta 100% basada en BD
import streamlit as st
import pandas as pd
import unicodedata
import os
from groq import Groq
from PIL import Image
import base64
import math

# Configuración de página - DEBE SER EL PRIMER COMANDO DE STREAMLIT
st.set_page_config(
    page_title="Bibliotecario Virtual",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# CONFIGURACIÓN DE TEMA OSCURO
# ==========================================

def configurar_tema_oscuro():
    """Configura el tema oscuro completo para toda la app"""
    st.markdown("""
    <style>
        /* Tema oscuro global */
        .stApp {
            background-color: #0e1117;
        }
        
        /* Sidebar oscuro */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
            border-right: 1px solid #2d2d44;
        }
        
        [data-testid="stSidebar"] * {
            color: #e0e0e0 !important;
        }
        
        /* Métricas en sidebar */
        [data-testid="stSidebar"] [data-testid="stMetricValue"] {
            color: #00ff9d !important;
        }
        
        [data-testid="stSidebar"] [data-testid="stMetricLabel"] {
            color: #888 !important;
        }
        
        /* Main content oscuro */
        .main .block-container {
            background-color: #0e1117;
        }
        
        /* Títulos */
        h1, h2, h3, h4, h5, h6 {
            color: #00ff9d !important;
            font-family: 'Share Tech Mono', monospace;
        }
        
        /* Texto normal */
        p, li, span, div {
            color: #e0e0e0 !important;
        }
        
        /* ========== INPUT DE CHAT PERFECTAMENTE CENTRADO ========== */
        .stChatInputContainer {
            width: 100%;
            display: flex;
            justify-content: center;
            margin: 0 auto;
        }
        
        .stChatInputContainer > div {
            width: 100%;
            max-width: 700px;
            margin: 0 auto;
        }
        
        div[data-testid="stChatInput"] {
            width: 100% !important;
            margin: 0 auto !important;
        }
        
        div[data-testid="stChatInput"] textarea {
            border-radius: 30px !important;
            background-color: #1e1e2e !important;
            border: 1px solid #2d2d44 !important;
            color: #e0e0e0 !important;
            font-size: 16px !important;
        }
        
        /* Ajuste para móviles */
        @media (max-width: 768px) {
            .stChatInputContainer > div {
                max-width: 95% !important;
                margin: 0 auto !important;
            }
            
            div[data-testid="stChatInput"] textarea {
                font-size: 16px !important;
                padding: 12px 16px !important;
            }
            
            .main .block-container {
                padding-left: 8px !important;
                padding-right: 8px !important;
            }
        }
        
        /* ========== RESPUESTA DEL BIBLIOTECARIO CENTRADA ========== */
        [data-testid="stChatMessage"] {
            max-width: 800px;
            margin: 0 auto 10px auto !important;
        }
        
        @media (max-width: 768px) {
            [data-testid="stChatMessage"] {
                max-width: 95% !important;
                margin: 0 auto 10px auto !important;
            }
        }
        
        /* Mensajes de chat */
        [data-testid="stChatMessage"] {
            background-color: #1e1e2e;
            border-radius: 10px;
        }
        
        /* ========== DISCLAIMER EXPERIMENTAL ========== */
        .experimental-badge {
            text-align: center;
            margin: 10px 0;
            padding: 8px;
            background: rgba(0,255,157,0.1);
            border-radius: 20px;
            font-size: 0.75rem;
            color: #00ff9d;
            border: 1px solid rgba(0,255,157,0.3);
            max-width: 300px;
            margin-left: auto;
            margin-right: auto;
        }
        
        /* Expander */
        .streamlit-expanderHeader {
            background-color: #1e1e2e;
            color: #00ff9d !important;
            border-radius: 8px;
        }
        
        /* Dataframe */
        .stDataFrame {
            background-color: #1e1e2e;
        }
        
        /* Info, warning, error boxes */
        .stAlert {
            background-color: #1e1e2e;
            border-left: 4px solid #00ff9d;
        }
        
        .stAlert p {
            color: #e0e0e0 !important;
        }
        
        /* Botones de paginación */
        .stButton button {
            background-color: #2d2d44;
            color: #00ff9d;
            border: none;
            border-radius: 8px;
            transition: all 0.3s ease;
        }
        
        .stButton button:hover {
            background-color: #3d3d5e;
            transform: scale(1.05);
        }
        
        /* Spinner */
        .stSpinner {
            color: #00ff9d;
        }
        
        /* Fuente geek */
        @import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&display=swap');
        
        body, .stApp {
            font-family: 'Share Tech Mono', monospace;
        }
        
        /* Scrollbar oscuro */
        ::-webkit-scrollbar {
            width: 8px;
            height: 8px;
        }
        
        ::-webkit-scrollbar-track {
            background: #1e1e2e;
        }
        
        ::-webkit-scrollbar-thumb {
            background: #2d2d44;
            border-radius: 4px;
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: #00ff9d;
        }
        
        /* Estilo para el footer SIMPLIFICADO */
        .footer {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            background: linear-gradient(90deg, #1a1a2e 0%, #16213e 100%);
            color: #00ff9d;
            text-align: center;
            padding: 0.5rem;
            font-size: 0.7rem;
            border-top: 1px solid #2d2d44;
            z-index: 999;
            font-family: 'Share Tech Mono', monospace;
            letter-spacing: 1px;
        }
        
        /* Ajuste para que el contenido no quede oculto detrás del footer */
        .main .block-container {
            padding-bottom: 50px;
        }
        
        /* Contenedor de paginación centrado */
        .pagination-container {
            display: flex;
            justify-content: center;
            gap: 10px;
            margin: 20px 0;
            flex-wrap: wrap;
        }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# FUNCIÓN PARA CARGAR LOGO
# ==========================================

def cargar_logo():
    """Carga el logo desde la carpeta images"""
    rutas_logo = [
        "images/logo.png",
        "images/logo.jpg",
        "images/logo.jpeg",
        "logo.png",
        "static/logo.png"
    ]
    
    for ruta in rutas_logo:
        if os.path.exists(ruta):
            try:
                img = Image.open(ruta)
                return ruta, img
            except Exception as e:
                continue
    
    return None, None

def mostrar_titulo_con_logo():
    """Muestra el título con el logo integrado"""
    ruta_logo, img = cargar_logo()
    
    if ruta_logo:
        with open(ruta_logo, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode()
        
        extension = ruta_logo.split('.')[-1].lower()
        mime_type = f"image/{extension}" if extension != 'jpg' else "image/jpeg"
        
        st.markdown(f"""
        <div style="display: flex; align-items: center; justify-content: center; margin: 20px 0 20px 0; gap: 15px; flex-wrap: wrap; text-align: center;">
            <img src="data:{mime_type};base64,{encoded_string}" 
                 style="width: 55px; height: 55px; border-radius: 12px; 
                        box-shadow: 0 0 15px rgba(0,255,157,0.3);
                        animation: pulse 2s infinite;">
            <div>
                <h1 style="margin: 0; color: #00ff9d; font-size: 2rem;">📖 Bibliotecario Virtual</h1>
                <p style="margin: 5px 0 0 0; color: #666; font-size: 0.8rem;">Búsqueda en catálogo local</p>
            </div>
        </div>
        <style>
            @keyframes pulse {{
                0% {{ box-shadow: 0 0 5px rgba(0,255,157,0.3); }}
                50% {{ box-shadow: 0 0 20px rgba(0,255,157,0.6); }}
                100% {{ box-shadow: 0 0 5px rgba(0,255,157,0.3); }}
            }}
        </style>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="display: flex; align-items: center; justify-content: center; margin: 20px 0 20px 0; gap: 15px; flex-wrap: wrap; text-align: center;">
            <div style="
                background: linear-gradient(135deg, #00ff9d, #0066cc);
                width: 55px;
                height: 55px;
                border-radius: 12px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 28px;
                box-shadow: 0 0 15px rgba(0,255,157,0.3);
                animation: pulse 2s infinite;
            ">
                📚
            </div>
            <div>
                <h1 style="margin: 0; color: #00ff9d; font-size: 2rem;">📖 Bibliotecario Virtual</h1>
                <p style="margin: 5px 0 0 0; color: #666; font-size: 0.8rem;">Búsqueda en catálogo local</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

def mostrar_footer():
    """Muestra el pie de página simplificado"""
    st.markdown("""
    <div class="footer">
        PISWD 2026
    </div>
    """, unsafe_allow_html=True)

def mostrar_disclaimer():
    """Muestra el disclaimer de modo experimental"""
    st.markdown("""
    <div class="experimental-badge">
        ⚡ MODO EXPERIMENTAL - Los resultados pueden ser parciales ⚡
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# FUNCIONES PRINCIPALES
# ==========================================

def normalizar(texto):
    """Limpia el texto de acentos, comillas y mayúsculas."""
    if not texto:
        return ""
    s = str(texto).replace('"', '').replace("'", "")
    return ''.join(
        c for c in unicodedata.normalize('NFD', s)
        if unicodedata.category(c) != 'Mn'
    ).lower().strip()

def extraer_apellidos(nombre_autor):
    """Extrae apellidos de un nombre de autor"""
    if not nombre_autor or pd.isna(nombre_autor):
        return []
    
    nombre_autor = str(nombre_autor)
    palabras = normalizar(nombre_autor).split()
    
    apellidos = []
    for i, palabra in enumerate(palabras):
        if i == len(palabras) - 1 or (len(palabra) > 3 and palabra[0].isupper()):
            apellidos.append(palabra)
    
    return apellidos

def cargar_datos():
    """Carga los datos desde data/BD.xlsx"""
    ruta_bd = "data/BD.xlsx"
    
    if os.path.exists(ruta_bd):
        try:
            df = pd.read_excel(ruta_bd)
            df.columns = [c.strip() for c in df.columns]
            
            if 'Ejemplares' not in df.columns:
                df['Ejemplares'] = 1
            else:
                df['Ejemplares'] = pd.to_numeric(df['Ejemplares'], errors='coerce').fillna(1).astype(int)
            
            return df
            
        except Exception as e:
            st.sidebar.error(f"Error al cargar BD: {e}")
            return None
    
    st.sidebar.error("❌ No se encontró el archivo data/BD.xlsx")
    return None

def busqueda_exhaustiva(termino, df):
    """Búsqueda flexible en la base de datos"""
    if df is None or df.empty:
        return []
    
    termino_norm = normalizar(termino)
    palabras_busqueda = termino_norm.split()
    
    resultados = []
    
    for idx, row in df.iterrows():
        puntaje = 0
        
        titulo = normalizar(row.get('Titulo', ''))
        autor = normalizar(row.get('Autor', ''))
        temas = normalizar(row.get('Temas', ''))
        subtemas = normalizar(row.get('SubTemas', ''))
        
        if termino_norm in titulo:
            puntaje += 100
        if termino_norm in autor:
            puntaje += 80
        
        apellidos_autor = extraer_apellidos(row.get('Autor', ''))
        for apellido in apellidos_autor:
            if apellido in termino_norm or termino_norm in apellido:
                puntaje += 70
        
        for palabra in palabras_busqueda:
            if len(palabra) > 2:
                if palabra in titulo:
                    puntaje += 20
                if palabra in autor:
                    puntaje += 25
                if palabra in temas:
                    puntaje += 15
                if palabra in subtemas:
                    puntaje += 10
        
        if puntaje > 0:
            resultados.append({
                'idx': idx,
                'puntaje': puntaje,
                'datos': row
            })
    
    resultados.sort(key=lambda x: x['puntaje'], reverse=True)
    return resultados

def mostrar_resultados_paginados(resultados, items_por_pagina=6):
    """Muestra resultados con paginación"""
    if not resultados:
        return
    
    total_resultados = len(resultados)
    total_paginas = math.ceil(total_resultados / items_por_pagina)
    
    # Inicializar página en session state
    if 'pagina_resultados' not in st.session_state:
        st.session_state.pagina_resultados = 0
    
    # Calcular índices
    inicio = st.session_state.pagina_resultados * items_por_pagina
    fin = min(inicio + items_por_pagina, total_resultados)
    
    # Mostrar resultados de la página actual
    st.markdown(f"**Mostrando {inicio + 1} - {fin} de {total_resultados} resultados**")
    
    cols = st.columns(2)
    for i, r in enumerate(resultados[inicio:fin]):
        with cols[i % 2]:
            datos = r['datos']
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, #1e1e2e 0%, #2d2d44 100%);
                padding: 1rem;
                border-radius: 12px;
                margin: 0.5rem 0;
                border-left: 4px solid #00ff9d;
                transition: transform 0.2s ease;
            ">
                <strong style="font-size: 1rem; color: #00ff9d;">📖 {datos['Titulo']}</strong><br>
                <span style="color: #aaa;">✍️ {datos['Autor']} ({datos['Año']})</span><br>
                <span style="color: #00ff9d;">📊 {datos['Ejemplares']} ejemplar(es)</span><br>
                <span style="color: #888; font-size: 0.8rem;">🏷️ {datos['Temas']}</span>
            </div>
            """, unsafe_allow_html=True)
    
    # Controles de paginación
    if total_paginas > 1:
        col1, col2, col3, col4, col5 = st.columns([1, 1, 2, 1, 1])
        
        with col2:
            if st.button("◀ Anterior", disabled=st.session_state.pagina_resultados == 0, key="prev_resultados"):
                st.session_state.pagina_resultados -= 1
                st.rerun()
        
        with col3:
            st.markdown(f"<p style='text-align: center;'>Página {st.session_state.pagina_resultados + 1} de {total_paginas}</p>", unsafe_allow_html=True)
        
        with col4:
            if st.button("Siguiente ▶", disabled=st.session_state.pagina_resultados >= total_paginas - 1, key="next_resultados"):
                st.session_state.pagina_resultados += 1
                st.rerun()

def mostrar_catalogo_paginado(df, items_por_pagina=15):
    """Muestra el catálogo completo con paginación"""
    if df is None or df.empty:
        return
    
    total_libros = len(df)
    total_paginas = math.ceil(total_libros / items_por_pagina)
    
    # Inicializar página en session state
    if 'pagina_catalogo' not in st.session_state:
        st.session_state.pagina_catalogo = 0
    
    # Calcular índices
    inicio = st.session_state.pagina_catalogo * items_por_pagina
    fin = min(inicio + items_por_pagina, total_libros)
    
    # Mostrar dataframe paginado
    st.markdown(f"**Mostrando {inicio + 1} - {fin} de {total_libros} libros**")
    df_pagina = df[['Id', 'Titulo', 'Autor', 'Año', 'Ejemplares', 'Temas']].iloc[inicio:fin]
    st.dataframe(df_pagina, use_container_width=True)
    
    # Controles de paginación
    if total_paginas > 1:
        col1, col2, col3, col4, col5 = st.columns([1, 1, 2, 1, 1])
        
        with col2:
            if st.button("◀ Anterior", disabled=st.session_state.pagina_catalogo == 0, key="prev_catalogo"):
                st.session_state.pagina_catalogo -= 1
                st.rerun()
        
        with col3:
            st.markdown(f"<p style='text-align: center;'>Página {st.session_state.pagina_catalogo + 1} de {total_paginas}</p>", unsafe_allow_html=True)
        
        with col4:
            if st.button("Siguiente ▶", disabled=st.session_state.pagina_catalogo >= total_paginas - 1, key="next_catalogo"):
                st.session_state.pagina_catalogo += 1
                st.rerun()
    
    st.caption(f"Total: {total_libros} libros")

def obtener_respuesta_groq(consulta, resultados, df):
    """Obtener respuesta de Groq con los resultados - SOLO USA RESULTADOS REALES"""
    try:
        api_key = st.secrets.get("GROQ_API_KEY")
        
        if not api_key:
            return "⚠️ Error: No se encontró la API key."
        
        client = Groq(api_key=api_key)
        
        if resultados:
            # Construir lista detallada de libros REALES
            libros_lista = []
            for r in resultados:
                datos = r['datos']
                libros_lista.append(
                    f"• {datos['Titulo']} - Autor: {datos['Autor']} ({datos['Año']}) - {datos['Ejemplares']} ejemplares - Tema: {datos['Temas']}"
                )
            
            # Crear contexto MUY ESTRICTO
            contexto = f"""
ESTOS SON LOS ÚNICOS LIBROS DISPONIBLES EN LA BIBLIOTECA QUE COINCIDEN CON LA BÚSQUEDA:

{chr(10).join(libros_lista)}

REGLAS ABSOLUTAS QUE DEBES SEGUIR ESTRICTAMENTE:
1. SOLO puedes mencionar los libros que están en la lista de arriba.
2. NO inventes ningún libro, autor, título o recomendación.
3. NO menciones libros que no estén en la lista.
4. Si el usuario pide recomendaciones, solo recomienda los libros de esta lista.
5. Si no hay libros sobre un tema específico, dices que no hay disponibles.
6. Tu respuesta debe basarse EXCLUSIVAMENTE en los libros listados arriba.
"""
        else:
            contexto = """
NO HAY LIBROS EN LA BASE DE DATOS QUE COINCIDAN CON ESTA BÚSQUEDA.

REGLAS:
1. Dile al usuario que no hay libros disponibles sobre ese tema.
2. NO inventes libros ni recomendaciones.
3. Sugiere que pruebe con otros términos de búsqueda como autor, tema o título parcial.
"""
        
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Eres un bibliotecario que trabaja en una biblioteca real. "
                        "SOLO respondes con los libros listados en el contexto. "
                        "Tu trabajo es ayudar al usuario a encontrar libros de la biblioteca. "
                        "NUNCA mencionas libros que no estén explícitamente en la lista. "
                        "Si el usuario pide recomendaciones sobre un tema, revisa los temas de los libros listados.\n\n"
                        f"{contexto}"
                    )
                },
                {
                    "role": "user",
                    "content": f"El usuario pregunta: '{consulta}'. Basándote SOLO en los libros listados en el contexto, responde de manera útil y precisa."
                }
            ],
            temperature=0.0,
            max_tokens=300
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"❌ Error: {str(e)}"

# ==========================================
# INTERFAZ PRINCIPAL
# ==========================================

def main():
    # Configurar tema oscuro
    configurar_tema_oscuro()
    
    # Mostrar título con logo integrado
    mostrar_titulo_con_logo()
    
    # Mostrar disclaimer experimental
    mostrar_disclaimer()
    
    # Sidebar
    with st.sidebar:
        st.markdown("""
        <div style="text-align: center; margin: 20px 0;">
            <span style="font-size: 48px;">📚</span>
            <h2 style="color: #00ff9d; margin: 10px 0;">Biblioteca</h2>
            <p style="color: #888;">Virtual Assistant</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        df = cargar_datos()
        
        if df is not None:
            st.markdown("### 📊 Estadísticas")
            col1, col2 = st.columns(2)
            with col1:
                st.metric("📚 Títulos", len(df))
            with col2:
                st.metric("📖 Ejemplares", df['Ejemplares'].sum())
            
            st.markdown("---")
            
            if 'Autor' in df.columns:
                st.markdown("### ✍️ Autores destacados")
                autores_top = df['Autor'].value_counts().head(5)
                for autor, count in autores_top.items():
                    if autor and autor != '':
                        st.write(f"• {autor[:30]} ({count})")
            
            st.markdown("---")
            
            if 'Temas' in df.columns:
                st.markdown("### 🏷️ Temas populares")
                temas_top = df['Temas'].value_counts().head(5)
                for tema, count in temas_top.items():
                    if tema and tema != '':
                        st.write(f"• {tema[:30]} ({count})")
            
            st.markdown("---")
            st.caption(f"📁 data/BD.xlsx")
    
    # Main content
    if df is None:
        st.error("❌ No se pudo cargar la base de datos")
        st.info("""
        ### 📋 Solución:
        1. Asegúrate de que el archivo **BD.xlsx** esté en la carpeta **data/**
        2. Verifica que tenga estas columnas:
           - Id, Titulo, Autor, Año, ISBN, Temas, SubTemas, Ejemplares, Ideas principales
        """)
        mostrar_footer()
        return
    
    # Catálogo con paginación
    with st.expander("📚 Ver catálogo completo", expanded=False):
        mostrar_catalogo_paginado(df, items_por_pagina=15)
    
    # Contenedor centrado para el chat input
    st.markdown('<div class="stChatInputContainer">', unsafe_allow_html=True)
    consulta = st.chat_input("🔍 Escribe tu consulta aquí...")
    st.markdown('</div>', unsafe_allow_html=True)
    
    if consulta:
        with st.chat_message("user"):
            st.write(consulta)
        
        with st.spinner("🔍 Buscando en la biblioteca..."):
            resultados = busqueda_exhaustiva(consulta, df)
        
        with st.chat_message("assistant"):
            if resultados:
                st.markdown("### 📚 Resultados encontrados:")
                
                # Mostrar resultados paginados
                mostrar_resultados_paginados(resultados, items_por_pagina=6)
                
                with st.spinner("💭 Generando respuesta basada en los libros de tu biblioteca..."):
                    respuesta = obtener_respuesta_groq(consulta, resultados, df)
                
                st.markdown("---")
                st.markdown("### 💬 Respuesta del bibliotecario:")
                st.info(f"📖 **Basado en los {len(resultados)} libros encontrados:**\n\n{respuesta}")
                
                if resultados:
                    st.caption(f"✨ Los libros mostrados arriba son los que tenemos en nuestra biblioteca. La respuesta se basa EXCLUSIVAMENTE en estos libros.")
                
            else:
                st.warning(f"❌ No encontré libros sobre '{consulta}' en nuestro catálogo.")
                st.markdown("""
                💡 **Sugerencias:**
                - Revisa la ortografía
                - Prueba con palabras más generales
                - Busca por autor o tema
                """)
    
    # Mostrar footer simplificado
    mostrar_footer()

if __name__ == "__main__":
    main()
