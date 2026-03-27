# app.py
import streamlit as st
import pandas as pd
import sqlite3
import unicodedata
import os
from groq import Groq
from datetime import datetime

# Configuración de la página
st.set_page_config(
    page_title="Bibliotecario Virtual",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS personalizados
st.markdown("""
<style>
    .stApp {
        max-width: 1200px;
        margin: 0 auto;
    }
    .result-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .book-title {
        font-size: 1.2rem;
        font-weight: bold;
        color: #0066cc;
    }
    .book-author {
        color: #666;
        font-style: italic;
    }
    .book-copies {
        color: #28a745;
        font-weight: bold;
    }
    .stats-box {
        background-color: #e3f2fd;
        padding: 1rem;
        border-radius: 0.5rem;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# FUNCIONES DE PROCESAMIENTO
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

@st.cache_data
def cargar_datos():
    """Carga los datos desde el archivo Excel (cacheado)"""
    # Buscar el archivo en diferentes ubicaciones
    posibles_rutas = [
        "data/biblioteca.xlsx",
        "biblioteca.xlsx",
        "libros.xlsx",
        "data/libros.xlsx"
    ]
    
    archivo_encontrado = None
    for ruta in posibles_rutas:
        if os.path.exists(ruta):
            archivo_encontrado = ruta
            break
    
    if not archivo_encontrado:
        st.error("""
        ❌ No se encontró el archivo de la biblioteca.
        
        **Instrucciones:**
        1. Sube tu archivo Excel en la barra lateral
        2. O asegúrate de tener un archivo 'biblioteca.xlsx' en la carpeta 'data/'
        """)
        
        # Permitir subir archivo desde la interfaz
        archivo_subido = st.sidebar.file_uploader(
            "📂 Sube tu archivo Excel",
            type=['xlsx', 'xls', 'csv']
        )
        
        if archivo_subido:
            if archivo_subido.name.endswith('.csv'):
                df = pd.read_csv(archivo_subido)
            else:
                df = pd.read_excel(archivo_subido)
            st.success(f"✅ Archivo cargado: {archivo_subido.name}")
            return df, archivo_subido.name
        else:
            return None, None
    
    # Cargar desde archivo local
    if archivo_encontrado.endswith('.csv'):
        df = pd.read_csv(archivo_encontrado)
    else:
        df = pd.read_excel(archivo_encontrado)
    
    # Limpiar nombres de columnas
    df.columns = [c.strip() for c in df.columns]
    
    # Verificar campos requeridos
    campos_requeridos = ['Id', 'Titulo', 'Autor', 'Año', 'ISBN', 'Temas', 'SubTemas', 'Ejemplares', 'Ideas principales']
    for campo in campos_requeridos:
        if campo not in df.columns:
            if campo == 'Ejemplares':
                df[campo] = 1
            else:
                df[campo] = ''
    
    # Asegurar que Ejemplares sea numérico
    df['Ejemplares'] = pd.to_numeric(df['Ejemplares'], errors='coerce').fillna(1).astype(int)
    
    return df, archivo_encontrado

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
        
        # Búsqueda por título exacto
        if termino_norm in titulo:
            puntaje += 100
            razones.append("título coincide")
        
        # Búsqueda por autor
        if termino_norm in autor:
            puntaje += 80
            razones.append("autor coincide")
        
        # Búsqueda por apellido
        apellidos_autor = extraer_apellidos(row.get('Autor', ''))
        for apellido in apellidos_autor:
            if apellido in termino_norm or termino_norm in apellido:
                puntaje += 70
                razones.append(f"apellido '{apellido}' coincide")
        
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
    api_key = st.secrets.get("GROQ_API_KEY", os.getenv("GROQ_API_KEY"))
    
    if not api_key:
        return "⚠️ Error: No se encontró la API key de Groq. Configúrala en los secrets de Streamlit."
    
    client = Groq(api_key=api_key)
    
    # Construir contexto según resultados
    if resultados:
        contexto_str = []
        for r in resultados[:10]:
            datos = r['datos']
            contexto_str.append(
                f"- {datos['Titulo']} | {datos['Autor']} ({datos['Año']}) | "
                f"Ejemplares: {datos['Ejemplares']} | Temas: {datos['Temas']}"
            )
        
        contexto = f"""
LIBROS ENCONTRADOS EN LA BASE DE DATOS:
{chr(10).join(contexto_str)}

INSTRUCCIÓN: SOLO puedes mencionar los libros listados arriba. NO inventes títulos.
"""
    else:
        contexto = "NO SE ENCONTRARON LIBROS EN LA BASE DE DATOS PARA ESTA BÚSQUEDA."
    
    # Llamar a Groq
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Eres un bibliotecario amable y servicial. "
                        "SOLO respondes con información de la base de datos proporcionada. "
                        "Si no hay resultados, dices que no hay libros sobre ese tema. "
                        "NUNCA inventas títulos ni autores."
                        f"\n\n{contexto}"
                    )
                },
                {
                    "role": "user",
                    "content": consulta
                }
            ],
            temperature=0.1,
            max_tokens=300
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"❌ Error al conectar con Groq: {str(e)}"

# ==========================================
# INTERFAZ PRINCIPAL
# ==========================================

def main():
    # Sidebar
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/2232/2232688.png", width=80)
        st.title("📚 Biblioteca Virtual")
        st.markdown("---")
        
        # Cargar datos
        df, archivo = cargar_datos()
        
        if df is not None:
            st.success(f"✅ Base de datos cargada")
            st.info(f"📊 **Estadísticas:**\n\n- {len(df)} títulos\n- {df['Ejemplares'].sum()} ejemplares")
            
            # Mostrar temas más comunes
            if 'Temas' in df.columns:
                st.markdown("---")
                st.subheader("🏷️ Temas disponibles")
                temas_count = df['Temas'].value_counts().head(10)
                for tema, count in temas_count.items():
                    if tema and tema != '':
                        st.write(f"- {tema} ({count})")
            
            # Opciones de filtro
            st.markdown("---")
            st.subheader("🔍 Filtros rápidos")
            
            # Filtro por autor
            autores = df['Autor'].dropna().unique()
            autor_seleccionado = st.selectbox("Autor", ["Todos"] + sorted(autores))
            
            if autor_seleccionado != "Todos":
                df_filtrado = df[df['Autor'] == autor_seleccionado]
                st.write(f"**{len(df_filtrado)}** libros de {autor_seleccionado}")
    
    # Main content
    st.title("📖 Bibliotecario Virtual")
    st.markdown("Pregúntame sobre los libros disponibles en nuestra biblioteca")
    
    # Input de consulta
    consulta = st.chat_input("Escribe tu consulta aquí...")
    
    if consulta:
        if df is None:
            st.error("❌ Primero debes cargar la base de datos en la barra lateral")
            return
        
        # Mostrar consulta del usuario
        with st.chat_message("user"):
            st.write(consulta)
        
        # Buscar en BD
        with st.spinner("🔍 Buscando en la biblioteca..."):
            resultados = busqueda_exhaustiva(consulta, df)
        
        # Mostrar resultados
        with st.chat_message("assistant"):
            if resultados:
                # Mostrar tabla de resultados
                st.markdown("### 📚 Resultados encontrados:")
                
                # Crear DataFrame para mostrar
                df_resultados = pd.DataFrame([r['datos'] for r in resultados])
                
                # Mostrar en columnas
                cols = st.columns(2)
                for idx, (i, row) in enumerate(df_resultados.head(6).iterrows()):
                    with cols[idx % 2]:
                        with st.container():
                            st.markdown(f"""
                            <div class="result-card">
                                <div class="book-title">📖 {row['Titulo']}</div>
                                <div class="book-author">✍️ {row['Autor']} ({row['Año']})</div>
                                <div class="book-copies">📊 {row['Ejemplares']} ejemplares</div>
                                <div>🏷️ {row['Temas']}</div>
                            </div>
                            """, unsafe_allow_html=True)
                
                # Mostrar estadísticas
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Títulos encontrados", len(resultados))
                with col2:
                    total_ejemplares = df_resultados['Ejemplares'].sum()
                    st.metric("Total ejemplares", total_ejemplares)
                with col3:
                    st.metric("Coincidencia", f"{resultados[0]['puntaje']}%")
                
                # Obtener respuesta de Groq
                with st.spinner("💭 Generando respuesta..."):
                    respuesta = obtener_respuesta_groq(consulta, resultados, df)
                
                st.markdown("### 💬 Respuesta del bibliotecario:")
                st.write(respuesta)
                
            else:
                st.warning(f"❌ No encontré libros sobre '{consulta}' en nuestro catálogo.")
                st.info("💡 **Sugerencias:**\n- Revisa la ortografía\n- Prueba con palabras más generales\n- Busca por autor o tema en lugar de título completo")

if __name__ == "__main__":
    main()
