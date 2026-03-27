
# app.py - Versión con logo
import streamlit as st
import pandas as pd
import unicodedata
import os
from groq import Groq
from PIL import Image
import base64
from pathlib import Path

# Configuración de página - DEBE SER EL PRIMER COMANDO DE STREAMLIT
st.set_page_config(
    page_title="Bibliotecario Virtual",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# FUNCIÓN PARA CARGAR LOGO
# ==========================================

def cargar_logo():
    """Carga el logo desde la carpeta images"""
    # Rutas posibles para el logo
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
                # Cargar imagen con PIL para verificar que es válida
                img = Image.open(ruta)
                return ruta, img
            except Exception as e:
                st.warning(f"No se pudo cargar el logo desde {ruta}: {e}")
                continue
    
    return None, None

def agregar_logo_css():
    """Agrega CSS personalizado para posicionar el logo en la esquina superior derecha"""
    st.markdown("""
    <style>
        /* Posicionar el logo en la esquina superior derecha */
        .logo-container {
            position: fixed;
            top: 0.5rem;
            right: 1rem;
            z-index: 999;
            display: flex;
            justify-content: flex-end;
            align-items: center;
            pointer-events: none; /* Permite hacer clic a través del logo */
        }
        
        .logo-img {
            max-width: 60px;
            max-height: 60px;
            width: auto;
            height: auto;
            border-radius: 10px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            transition: transform 0.3s ease;
            pointer-events: auto; /* Permite interactuar con el logo si es necesario */
        }
        
        .logo-img:hover {
            transform: scale(1.05);
        }
        
        /* Ajustes para móviles */
        @media (max-width: 768px) {
            .logo-img {
                max-width: 45px;
                max-height: 45px;
            }
        }
        
        /* Ajuste para evitar que el logo cubra contenido importante */
        .main-header {
            margin-top: 0;
            padding-top: 0;
        }
        
        /* Ajuste del título principal para dar espacio al logo */
        .stApp header {
            background-color: transparent;
        }
        
        /* Personalización del sidebar */
        [data-testid="stSidebar"] {
            background-color: #f8f9fa;
        }
    </style>
    """, unsafe_allow_html=True)

def mostrar_logo():
    """Muestra el logo en la esquina superior derecha usando HTML"""
    ruta_logo, img = cargar_logo()
    
    if ruta_logo:
        # Convertir imagen a base64 para mostrarla en HTML
        with open(ruta_logo, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode()
        
        # Determinar el tipo de imagen
        extension = ruta_logo.split('.')[-1].lower()
        mime_type = f"image/{extension}" if extension != 'jpg' else "image/jpeg"
        
        # HTML para mostrar el logo
        logo_html = f"""
        <div class="logo-container">
            <img src="data:{mime_type};base64,{encoded_string}" 
                 class="logo-img" 
                 alt="Logo Biblioteca"
                 title="Biblioteca Virtual">
        </div>
        """
        st.markdown(logo_html, unsafe_allow_html=True)
    else:
        # Logo por defecto si no se encuentra el archivo
        st.markdown("""
        <div class="logo-container">
            <div style="
                background-color: #0066cc;
                color: white;
                width: 50px;
                height: 50px;
                border-radius: 10px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 24px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
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
    
    # Ruta específica para tu archivo
    ruta_bd = "data/BD.xlsx"
    
    # Verificar si existe el archivo
    if os.path.exists(ruta_bd):
        try:
            df = pd.read_excel(ruta_bd)
            
            # Limpiar nombres de columnas
            df.columns = [c.strip() for c in df.columns]
            
            # Verificar campos
            if 'Ejemplares' not in df.columns:
                df['Ejemplares'] = 1
            else:
                df['Ejemplares'] = pd.to_numeric(df['Ejemplares'], errors='coerce').fillna(1).astype(int)
            
            return df
            
        except Exception as e:
            st.sidebar.error(f"Error al cargar BD: {e}")
            return None
    
    # Si no existe el archivo, mostrar error
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
        razones = []
        
        titulo = normalizar(row.get('Titulo', ''))
        autor = normalizar(row.get('Autor', ''))
        temas = normalizar(row.get('Temas', ''))
        subtemas = normalizar(row.get('SubTemas', ''))
        
        # Búsqueda por título
        if termino_norm in titulo:
            puntaje += 100
            razones.append("título")
        
        # Búsqueda por autor
        if termino_norm in autor:
            puntaje += 80
            razones.append("autor")
        
        # Búsqueda por apellido
        apellidos_autor = extraer_apellidos(row.get('Autor', ''))
        for apellido in apellidos_autor:
            if apellido in termino_norm or termino_norm in apellido:
                puntaje += 70
                razones.append(f"apellido '{apellido}'")
        
        # Búsqueda por palabras individuales
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
                'razones': razones,
                'datos': row
            })
    
    resultados.sort(key=lambda x: x['puntaje'], reverse=True)
    return resultados[:15]

def obtener_respuesta_groq(consulta, resultados, df):
    """Obtener respuesta de Groq con los resultados"""
    try:
        # Obtener API key de secrets
        api_key = st.secrets.get("GROQ_API_KEY")
        
        if not api_key:
            return "⚠️ Error: No se encontró la API key. Configúrala en Streamlit Secrets."
        
        client = Groq(api_key=api_key)
        
        # Construir contexto
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
        
        # Llamar a Groq
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
    # Aplicar CSS para el logo
    agregar_logo_css()
    
    # Mostrar el logo en la esquina superior derecha
    mostrar_logo()
    
    # Sidebar
    with st.sidebar:
        # Logo pequeño en el sidebar también (opcional)
        st.markdown("""
        <div style="text-align: center; margin-bottom: 20px;">
            <span style="font-size: 40px;">📚</span>
        </div>
        """, unsafe_allow_html=True)
        
        st.title("Biblioteca Virtual")
        st.markdown("---")
        
        # Cargar datos desde data/BD.xlsx
        df = cargar_datos()
        
        if df is not None:
            st.markdown("### 📊 Estadísticas")
            col1, col2 = st.columns(2)
            with col1:
                st.metric("📚 Títulos", len(df))
            with col2:
                st.metric("📖 Ejemplares", df['Ejemplares'].sum())
            
            st.markdown("---")
            
            # Mostrar autores destacados
            if 'Autor' in df.columns:
                st.markdown("### ✍️ Autores destacados")
                autores_top = df['Autor'].value_counts().head(5)
                for autor, count in autores_top.items():
                    if autor and autor != '':
                        st.write(f"• {autor[:30]} ({count})")
            
            st.markdown("---")
            
            # Mostrar temas populares
            if 'Temas' in df.columns:
                st.markdown("### 🏷️ Temas populares")
                temas_top = df['Temas'].value_counts().head(5)
                for tema, count in temas_top.items():
                    if tema and tema != '':
                        st.write(f"• {tema[:30]} ({count})")
            
            st.markdown("---")
            st.caption(f"📁 Fuente: data/BD.xlsx")
    
    # Main content
    st.title("📖 Bibliotecario Virtual")
    st.markdown("Pregúntame sobre los libros disponibles en nuestra biblioteca")
    
    if df is None:
        st.error("❌ No se pudo cargar la base de datos")
        st.info("""
        ### 📋 Solución:
        1. Asegúrate de que el archivo **BD.xlsx** esté en la carpeta **data/**
        2. Verifica que tenga estas columnas:
           - Id
           - Titulo
           - Autor
           - Año
           - ISBN
           - Temas
           - SubTemas
           - Ejemplares
           - Ideas principales
        """)
        return
    
    # Vista previa del catálogo
    with st.expander("📚 Ver catálogo completo", expanded=False):
        df_preview = df[['Id', 'Titulo', 'Autor', 'Año', 'Ejemplares', 'Temas']].head(20)
        st.dataframe(df_preview, use_container_width=True)
        st.caption(f"Mostrando 20 de {len(df)} libros totales")
    
    # Input de consulta
    consulta = st.chat_input("🔍 Escribe tu consulta aquí...")
    
    if consulta:
        # Mostrar consulta del usuario
        with st.chat_message("user"):
            st.write(consulta)
        
        # Buscar en BD
        with st.spinner("🔍 Buscando en la biblioteca..."):
            resultados = busqueda_exhaustiva(consulta, df)
        
        # Mostrar resultados
        with st.chat_message("assistant"):
            if resultados:
                st.markdown("### 📚 Resultados encontrados:")
                
                # Mostrar en tarjetas
                cols = st.columns(2)
                for i, r in enumerate(resultados[:6]):
                    with cols[i % 2]:
                        datos = r['datos']
                        st.markdown(f"""
                        <div style="
                            background-color: #f8f9fa;
                            padding: 0.8rem;
                            border-radius: 0.5rem;
                            margin: 0.5rem 0;
                            border-left: 4px solid #0066cc;
                            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                        ">
                            <strong style="font-size: 1rem;">📖 {datos['Titulo']}</strong><br>
                            <span style="color: #666;">✍️ {datos['Autor']} ({datos['Año']})</span><br>
                            <span style="color: #28a745;">📊 {datos['Ejemplares']} ejemplar(es)</span><br>
                            <span style="color: #888; font-size: 0.8rem;">🏷️ {datos['Temas']}</span>
                        </div>
                        """, unsafe_allow_html=True)
                
                # Obtener respuesta de Groq
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

def agregar_logo_css():
    """Agrega CSS personalizado con estilo geek"""
    st.markdown("""
    <style>
        /* Estilo geek para el logo */
        .logo-container {
            position: fixed;
            top: 0.5rem;
            right: 1rem;
            z-index: 999;
        }
        
        .logo-img {
            max-width: 70px;
            max-height: 70px;
            border-radius: 15px;
            box-shadow: 0 0 15px rgba(0,102,204,0.3);
            transition: all 0.3s ease;
            filter: drop-shadow(0 0 5px #0066cc);
            animation: pulse 2s infinite;
        }
        
        .logo-img:hover {
            transform: rotate(5deg) scale(1.1);
            filter: drop-shadow(0 0 10px #0066cc);
        }
        
        @keyframes pulse {
            0% {
                filter: drop-shadow(0 0 2px #0066cc);
            }
            50% {
                filter: drop-shadow(0 0 10px #0066cc);
            }
            100% {
                filter: drop-shadow(0 0 2px #0066cc);
            }
        }
        
        /* Efecto matrix para el fondo del sidebar (opcional) */
        [data-testid="stSidebar"] {
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: #0f0;
        }
        
        /* Fuente geek para títulos */
        @import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&display=swap');
        
        h1, h2, h3 {
            font-family: 'Share Tech Mono', monospace;
            letter-spacing: 2px;
        }
    </style>
    """, unsafe_allow_html=True)
