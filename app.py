# app.py - Versión con ruta específica data/BD.xlsx
import streamlit as st
import pandas as pd
import unicodedata
import os
from groq import Groq

# Configuración de página
st.set_page_config(
    page_title="Bibliotecario Virtual",
    page_icon="📚",
    layout="wide"
)

# ==========================================
# FUNCIONES
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
            
            st.sidebar.success(f"✅ BD cargada desde data/BD.xlsx")
            st.sidebar.info(f"📊 {len(df)} libros | {df['Ejemplares'].sum()} ejemplares")
            return df
            
        except Exception as e:
            st.sidebar.error(f"Error al cargar BD: {e}")
            return None
    
    # Si no existe el archivo, mostrar error
    st.sidebar.error("❌ No se encontró el archivo data/BD.xlsx")
    st.sidebar.info("💡 Asegúrate de que el archivo esté en la carpeta 'data' con el nombre 'BD.xlsx'")
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
            return "⚠️ Error: No se encontró la API key. Configúrala en Streamlit Secrets (Settings → Secrets)."
        
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
            temperature=0.0,  # Temperatura 0 para máxima precisión
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
        st.title("📚 Biblioteca Virtual")
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
        
        # Mostrar estructura de archivos actual
        import os
        st.markdown("### 📂 Estructura de archivos detectada:")
        for root, dirs, files in os.walk("."):
            level = root.replace(".", "").count(os.sep)
            indent = " " * 2 * level
            st.text(f"{indent}📁 {os.path.basename(root)}/")
            subindent = " " * 2 * (level + 1)
            for file in files[:10]:  # Mostrar primeros 10 archivos
                st.text(f"{subindent}📄 {file}")
        return
    
    # Vista previa del catálogo
    with st.expander("📚 Ver catálogo completo", expanded=False):
        # Mostrar tabla con los primeros libros
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
                
                # Mostrar nivel de coincidencia
                if resultados:
                    st.caption(f"✨ Mejor coincidencia: {resultados[0]['puntaje']}%")
                
            else:
                st.warning(f"❌ No encontré libros sobre '{consulta}' en nuestro catálogo.")
                
                # Sugerencias
                st.markdown("""
                💡 **Sugerencias:**
                - Revisa la ortografía de tu búsqueda
                - Prueba con palabras más generales
                - Busca por autor en lugar de título completo
                - Busca por tema o categoría
                """)

if __name__ == "__main__":
    main()
