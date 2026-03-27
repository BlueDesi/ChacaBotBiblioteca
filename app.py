
# app.py - Versión con tema oscuro y logo
import streamlit as st
import pandas as pd
import unicodedata
import os
from groq import Groq
from PIL import Image
import base64

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
        
        [data-testid="stSidebar"] .stMarkdown {
            color: #e0e0e0;
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
        
        /* Input de chat */
        [data-testid="stChatInput"] {
            background-color: #1e1e2e;
            border: 1px solid #2d2d44;
            color: #e0e0e0;
        }
        
        /* Mensajes de chat */
        [data-testid="stChatMessage"] {
            background-color: #1e1e2e;
            border-radius: 10px;
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
        
        /* Botones */
        .stButton button {
            background-color: #2d2d44;
            color: #00ff9d;
            border: none;
            border-radius: 8px;
        }
        
        .stButton button:hover {
            background-color: #3d3d5e;
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

def mostrar_logo():
    """Muestra el logo en la esquina superior derecha"""
    ruta_logo, img = cargar_logo()
    
    if ruta_logo:
        with open(ruta_logo, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode()
        
        extension = ruta_logo.split('.')[-1].lower()
        mime_type = f"image/{extension}" if extension != 'jpg' else "image/jpeg"
        
        logo_html = f"""
        <div style="position: fixed; top: 0.5rem; right: 1rem; z-index: 999;">
            <img src="data:{mime_type};base64,{encoded_string}" 
                 style="max-width: 60px; max-height: 60px; border-radius: 12px; 
                        box-shadow: 0 0 15px rgba(0,255,157,0.3);
                        transition: transform 0.3s ease;
                        animation: pulse 2s infinite;"
                 alt="Logo Biblioteca"
                 title="Biblioteca Virtual"
                 onmouseover="this.style.transform='scale(1.05)'"
                 onmouseout="this.style.transform='scale(1)'">
        </div>
        <style>
            @keyframes pulse {{
                0% {{ box-shadow: 0 0 5px rgba(0,255,157,0.3); }}
                50% {{ box-shadow: 0 0 20px rgba(0,255,157,0.6); }}
                100% {{ box-shadow: 0 0 5px rgba(0,255,157,0.3); }}
            }}
        </style>
        """
        st.markdown(logo_html, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="position: fixed; top: 0.5rem; right: 1rem; z-index: 999;">
            <div style="
                background: linear-gradient(135deg, #00ff9d, #0066cc);
                color: #0e1117;
                width: 55px;
                height: 55px;
                border-radius: 12px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 28px;
                font-weight: bold;
                box-shadow: 0 0 15px rgba(0,255,157,0.3);
                animation: pulse 2s infinite;
            ">
                📚
            </div>
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
    return resultados[:15]

def obtener_respuesta_groq(consulta, resultados, df):
    """Obtener respuesta de Groq con los resultados"""
    try:
        api_key = st.secrets.get("GROQ_API_KEY")
        
        if not api_key:
            return "⚠️ Error: No se encontró la API key. Configúrala en Streamlit Secrets."
        
        client = Groq(api_key=api_key)
        
        if resultados:
            contexto_str = []
            for r in resultados[:10]:
                datos = r['datos']
                contexto_str.append(
                    f"- TÍTULO: {datos['Titulo']} | AUTOR: {datos['Autor']} ({datos['Año']}) | "
                    f"EJEMPLARES: {datos['Ejemplares']} | TEMAS: {datos['Temas']}"
                )
            
            contexto = f"""
LIBROS ENCONTRADOS EN LA BASE DE DATOS:
{chr(10).join(contexto_str)}

INSTRUCCIÓN ESTRICTA: 
- SOLO puedes mencionar los libros listados arriba.
- NO inventes títulos, autores o temas.
- Si el usuario pregunta por algo que no está en esta lista, dile que no está disponible.
"""
        else:
            contexto = "NO SE ENCONTRARON LIBROS EN LA BASE DE DATOS PARA ESTA BÚSQUEDA."
        
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Eres un bibliotecario amable y servicial. "
                        "SOLO respondes con información de la base de datos proporcionada. "
                        "Si no hay resultados, dices claramente que no hay libros sobre ese tema. "
                        "NUNCA inventas títulos, autores ni sugerencias fuera del catálogo.\n\n"
                        f"{contexto}"
                    )
                },
                {
                    "role": "user",
                    "content": consulta
                }
            ],
            temperature=0.0,
            max_tokens=300
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"❌ Error al conectar con Groq: {str(e)}"

# ==========================================
# INTERFAZ PRINCIPAL
# ==========================================

def main():
    # Configurar tema oscuro
    configurar_tema_oscuro()
    
    # Mostrar el logo en la esquina superior derecha
    mostrar_logo()
    
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
    st.markdown("""
    <div style="text-align: center; margin: 20px 0 40px 0;">
        <h1>📖 Bibliotecario Virtual</h1>
        <p style="color: #888;">Pregúntame sobre los libros disponibles en nuestra biblioteca</p>
    </div>
    """, unsafe_allow_html=True)
    
    if df is None:
        st.error("❌ No se pudo cargar la base de datos")
        st.info("""
        ### 📋 Solución:
        1. Asegúrate de que el archivo **BD.xlsx** esté en la carpeta **data/**
        2. Verifica que tenga estas columnas:
           - Id, Titulo, Autor, Año, ISBN, Temas, SubTemas, Ejemplares, Ideas principales
        """)
        return
    
    with st.expander("📚 Ver catálogo completo", expanded=False):
        df_preview = df[['Id', 'Titulo', 'Autor', 'Año', 'Ejemplares', 'Temas']].head(20)
        st.dataframe(df_preview, use_container_width=True)
        st.caption(f"Mostrando 20 de {len(df)} libros totales")
    
    consulta = st.chat_input("🔍 Escribe tu consulta aquí...")
    
    if consulta:
        with st.chat_message("user"):
            st.write(consulta)
        
        with st.spinner("🔍 Buscando en la biblioteca..."):
            resultados = busqueda_exhaustiva(consulta, df)
        
        with st.chat_message("assistant"):
            if resultados:
                st.markdown("### 📚 Resultados encontrados:")
                
                cols = st.columns(2)
                for i, r in enumerate(resultados[:6]):
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
                
                with st.spinner("💭 Generando respuesta..."):
                    respuesta = obtener_respuesta_groq(consulta, resultados, df)
                
                st.markdown("---")
                st.markdown("### 💬 Respuesta del bibliotecario:")
                st.info(respuesta)
                
                if resultados:
                    st.caption(f"✨ Mejor coincidencia: {resultados[0]['puntaje']}%")
                
            else:
                st.warning(f"❌ No encontré libros sobre '{consulta}' en nuestro catálogo.")
                st.markdown("""
                💡 **Sugerencias:**
                - Revisa la ortografía de tu búsqueda
                - Prueba con palabras más generales
                - Busca por autor en lugar de título completo
                - Busca por tema o categoría
                """)

if __name__ == "__main__":
    main()
