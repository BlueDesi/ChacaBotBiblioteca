# app.py - Versión definitiva CORREGIDA con feedback funcionando
import streamlit as st
import pandas as pd
import unicodedata
import os
from groq import Groq
from PIL import Image
import base64
import math
from datetime import datetime, timedelta
import json
from collections import defaultdict
import time
import uuid

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
        
        /* Estilo para el footer */
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
        
        /* Estilo para métricas en la página */
        .metric-card {
            background: linear-gradient(135deg, #1e1e2e 0%, #2d2d44 100%);
            border-radius: 15px;
            padding: 1rem;
            text-align: center;
            border-left: 4px solid #00ff9d;
            margin: 0.5rem;
        }
        
        .metric-value {
            font-size: 2rem;
            font-weight: bold;
            color: #00ff9d;
        }
        
        .metric-label {
            font-size: 0.8rem;
            color: #888;
        }
        
        .country-badge {
            display: inline-block;
            background: #2d2d44;
            border-radius: 20px;
            padding: 0.3rem 0.8rem;
            margin: 0.2rem;
            font-size: 0.8rem;
        }
        
        /* Estilo para feedback */
        .feedback-container {
            background: rgba(0,255,157,0.05);
            border-radius: 10px;
            padding: 1rem;
            margin-top: 1rem;
            border: 1px solid rgba(0,255,157,0.2);
        }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# SISTEMA DE MÉTRICAS
# ==========================================

class MetricasSistema:
    """Clase para manejar las métricas de uso del sistema"""
    
    def __init__(self):
        self.archivo_metricas = "data/metricas.json"
        self.cargar_metricas()
    
    def cargar_metricas(self):
        """Carga las métricas desde archivo JSON"""
        if os.path.exists(self.archivo_metricas):
            try:
                with open(self.archivo_metricas, 'r', encoding='utf-8') as f:
                    self.metricas = json.load(f)
            except:
                self.inicializar_metricas()
        else:
            self.inicializar_metricas()
    
    def inicializar_metricas(self):
        """Inicializa la estructura de métricas"""
        self.metricas = {
            'consultas_totales': 0,
            'consultas_por_dia': {},
            'paises_acceso': {},
            'ciudades_acceso': {},
            'terminos_buscados': [],
            'consultas_con_resultados': 0,
            'consultas_sin_resultados': 0,
            'ultimas_consultas': [],
            'sesiones': {}
        }
        self.guardar_metricas()
    
    def guardar_metricas(self):
        """Guarda las métricas en archivo JSON"""
        try:
            os.makedirs("data", exist_ok=True)
            with open(self.archivo_metricas, 'w', encoding='utf-8') as f:
                json.dump(self.metricas, f, ensure_ascii=False, indent=2)
        except Exception as e:
            st.error(f"Error al guardar métricas: {e}")
    
    def registrar_consulta(self, termino, tuvo_resultados, session_id, ip_info=None):
        """Registra una nueva consulta en las métricas"""
        hoy = datetime.now().strftime("%Y-%m-%d")
        
        # Incrementar consultas totales
        self.metricas['consultas_totales'] += 1
        
        # Registrar por día
        if hoy not in self.metricas['consultas_por_dia']:
            self.metricas['consultas_por_dia'][hoy] = 0
        self.metricas['consultas_por_dia'][hoy] += 1
        
        # Registrar términos buscados
        self.metricas['terminos_buscados'].append({
            'termino': termino,
            'fecha': datetime.now().isoformat(),
            'resultados': tuvo_resultados
        })
        
        # Mantener solo las últimas 100 consultas
        if len(self.metricas['terminos_buscados']) > 100:
            self.metricas['terminos_buscados'] = self.metricas['terminos_buscados'][-100:]
        
        # Registrar resultados
        if tuvo_resultados:
            self.metricas['consultas_con_resultados'] += 1
        else:
            self.metricas['consultas_sin_resultados'] += 1
        
        # Registrar última consulta
        self.metricas['ultimas_consultas'].append({
            'termino': termino,
            'fecha': datetime.now().isoformat(),
            'resultados': tuvo_resultados
        })
        
        # Mantener solo últimas 20 consultas
        if len(self.metricas['ultimas_consultas']) > 20:
            self.metricas['ultimas_consultas'] = self.metricas['ultimas_consultas'][-20:]
        
        # Registrar ubicación si está disponible
        if ip_info:
            pais = ip_info.get('country', 'Desconocido')
            ciudad = ip_info.get('city', 'Desconocida')
            
            if pais not in self.metricas['paises_acceso']:
                self.metricas['paises_acceso'][pais] = 0
            self.metricas['paises_acceso'][pais] += 1
            
            if ciudad not in self.metricas['ciudades_acceso']:
                self.metricas['ciudades_acceso'][ciudad] = 0
            self.metricas['ciudades_acceso'][ciudad] += 1
        
        # Registrar sesión
        if session_id not in self.metricas['sesiones']:
            self.metricas['sesiones'][session_id] = {
                'primera_visita': datetime.now().isoformat(),
                'consultas': 0
            }
        self.metricas['sesiones'][session_id]['consultas'] += 1
        self.metricas['sesiones'][session_id]['ultima_consulta'] = datetime.now().isoformat()
        
        self.guardar_metricas()
    
    def obtener_metricas_ultimas_24h(self):
        """Obtiene métricas de las últimas 24 horas"""
        ahora = datetime.now()
        hace_24h = ahora - timedelta(hours=24)
        
        # Filtrar consultas últimas 24h
        consultas_24h = [c for c in self.metricas['terminos_buscados'] 
                        if datetime.fromisoformat(c['fecha']) > hace_24h]
        
        return {
            'total_consultas': len(consultas_24h),
            'consultas_con_resultados': sum(1 for c in consultas_24h if c['resultados']),
            'consultas_sin_resultados': sum(1 for c in consultas_24h if not c['resultados']),
            'terminos_populares': self.obtener_terminos_populares(consultas_24h),
            'paises': self.metricas['paises_acceso']
        }
    
    def obtener_terminos_populares(self, consultas, limite=10):
        """Obtiene los términos más buscados"""
        from collections import Counter
        terminos = [c['termino'] for c in consultas]
        return Counter(terminos).most_common(limite)

# ==========================================
# SISTEMA DE FEEDBACK - CORREGIDO
# ==========================================

class SistemaFeedback:
    """Clase para manejar feedback de usuarios"""
    
    def __init__(self):
        self.archivo_feedback = "data/feedback.json"
        self.archivo_comentarios = "data/comentarios_feedback.txt"
        self.cargar_feedback()
    
    def cargar_feedback(self):
        """Carga feedback existente"""
        if os.path.exists(self.archivo_feedback):
            try:
                with open(self.archivo_feedback, 'r', encoding='utf-8') as f:
                    self.feedback_data = json.load(f)
                # Debug: Mostrar en consola que se cargó
                print(f"Feedback cargado: {self.feedback_data['total_feedback']} feedbacks")
            except Exception as e:
                print(f"Error cargando feedback: {e}")
                self.inicializar_feedback()
        else:
            print("Creando nuevo archivo de feedback")
            self.inicializar_feedback()
    
    def inicializar_feedback(self):
        """Inicializa estructura de feedback"""
        self.feedback_data = {
            'total_feedback': 0,
            'util': 0,
            'no_util': 0,
            'tasa_efectividad': 0,
            'feedback_por_consulta': [],
            'estadisticas_por_termino': {},
            'ultimos_feedback': []
        }
        self.guardar_feedback()
    
    def guardar_feedback(self):
        """Guarda feedback en JSON"""
        try:
            os.makedirs("data", exist_ok=True)
            with open(self.archivo_feedback, 'w', encoding='utf-8') as f:
                json.dump(self.feedback_data, f, ensure_ascii=False, indent=2)
            print(f"Feedback guardado: {self.feedback_data['total_feedback']} total, {self.feedback_data['util']} útil, {self.feedback_data['no_util']} no útil")
            return True
        except Exception as e:
            print(f"Error al guardar feedback: {e}")
            return False
    
    def guardar_comentario(self, consulta, termino, comentario):
        """Guarda comentario adicional en archivo de texto"""
        try:
            os.makedirs("data", exist_ok=True)
            with open(self.archivo_comentarios, 'a', encoding='utf-8') as f:
                f.write(f"\n{'='*60}\n")
                f.write(f"Fecha: {datetime.now().isoformat()}\n")
                f.write(f"Consulta original: {consulta}\n")
                f.write(f"Término buscado: {termino}\n")
                f.write(f"Comentario: {comentario}\n")
                f.write(f"{'='*60}\n")
            return True
        except Exception as e:
            print(f"Error al guardar comentario: {e}")
            return False
    
    def registrar_feedback(self, consulta, termino, util, resultados_count, respuesta, comentario=None):
        """Registra feedback del usuario"""
        
        print(f"Registrando feedback: {termino} - Util: {util}")
        
        # Actualizar contadores
        self.feedback_data['total_feedback'] += 1
        
        if util:
            self.feedback_data['util'] += 1
        else:
            self.feedback_data['no_util'] += 1
        
        # Calcular tasa de efectividad
        if self.feedback_data['total_feedback'] > 0:
            self.feedback_data['tasa_efectividad'] = (
                self.feedback_data['util'] / self.feedback_data['total_feedback'] * 100
            )
        
        # Registrar feedback individual
        feedback_item = {
            'fecha': datetime.now().isoformat(),
            'consulta': consulta,
            'termino_buscado': termino,
            'util': util,
            'resultados_encontrados': resultados_count,
            'respuesta_generada': respuesta[:300] + "..." if len(respuesta) > 300 else respuesta
        }
        
        self.feedback_data['feedback_por_consulta'].append(feedback_item)
        
        # Mantener solo últimos 200 feedbacks
        if len(self.feedback_data['feedback_por_consulta']) > 200:
            self.feedback_data['feedback_por_consulta'] = self.feedback_data['feedback_por_consulta'][-200:]
        
        # Actualizar estadísticas por término
        if termino not in self.feedback_data['estadisticas_por_termino']:
            self.feedback_data['estadisticas_por_termino'][termino] = {
                'util': 0,
                'no_util': 0,
                'total': 0
            }
        
        if util:
            self.feedback_data['estadisticas_por_termino'][termino]['util'] += 1
        else:
            self.feedback_data['estadisticas_por_termino'][termino]['no_util'] += 1
        
        self.feedback_data['estadisticas_por_termino'][termino]['total'] += 1
        
        # Últimos feedbacks
        self.feedback_data['ultimos_feedback'].append({
            'fecha': datetime.now().isoformat(),
            'termino': termino,
            'util': util
        })
        
        if len(self.feedback_data['ultimos_feedback']) > 50:
            self.feedback_data['ultimos_feedback'] = self.feedback_data['ultimos_feedback'][-50:]
        
        # Guardar en disco
        self.guardar_feedback()
        
        # Guardar comentario si existe
        if comentario and comentario.strip():
            self.guardar_comentario(consulta, termino, comentario)
        
        return True
    
    def obtener_metricas_feedback(self):
        """Obtiene métricas de feedback"""
        return {
            'total': self.feedback_data['total_feedback'],
            'util': self.feedback_data['util'],
            'no_util': self.feedback_data['no_util'],
            'tasa_efectividad': self.feedback_data['tasa_efectividad'],
            'terminos_problematicos': self.obtener_terminos_problematicos(),
            'terminos_exitosos': self.obtener_terminos_exitosos()
        }
    
    def obtener_terminos_problematicos(self, limite=5):
        """Obtiene términos con más feedback negativo"""
        problematicos = []
        for termino, stats in self.feedback_data['estadisticas_por_termino'].items():
            if stats['total'] >= 2:
                tasa_no_util = stats['no_util'] / stats['total'] * 100
                problematicos.append((termino, tasa_no_util, stats['no_util'], stats['total']))
        
        problematicos.sort(key=lambda x: x[1], reverse=True)
        return problematicos[:limite]
    
    def obtener_terminos_exitosos(self, limite=5):
        """Obtiene términos con mejor feedback"""
        exitosos = []
        for termino, stats in self.feedback_data['estadisticas_por_termino'].items():
            if stats['total'] >= 2:
                tasa_util = stats['util'] / stats['total'] * 100
                exitosos.append((termino, tasa_util, stats['util'], stats['total']))
        
        exitosos.sort(key=lambda x: x[1], reverse=True)
        return exitosos[:limite]

# Inicializar sistemas
metricas_sistema = MetricasSistema()
feedback_sistema = SistemaFeedback()

def obtener_informacion_ip():
    """Intenta obtener información de IP usando API gratuita"""
    try:
        import requests
        response = requests.get('https://ipapi.co/json/', timeout=2)
        if response.status_code == 200:
            data = response.json()
            return {
                'country': data.get('country_name', 'Desconocido'),
                'city': data.get('city', 'Desconocida'),
                'ip': data.get('ip', 'unknown')
            }
    except:
        pass
    return None

# ==========================================
# FUNCIONES DE INTERFAZ
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
    """Muestra el pie de página"""
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

def mostrar_botones_feedback(consulta_original, termino_buscado, resultados_count, respuesta_generada):
    """Muestra botones de feedback después de cada respuesta - CORREGIDO"""
    
    # Usar un ID único basado en timestamp + consulta para cada feedback
    feedback_id = f"fb_{int(time.time() * 1000)}_{hash(consulta_original) % 10000}"
    
    # Verificar si ya se dio feedback para esta consulta
    if feedback_id not in st.session_state:
        st.session_state[feedback_id] = False
    
    if not st.session_state[feedback_id]:
        st.markdown('<div class="feedback-container">', unsafe_allow_html=True)
        st.markdown("### 📝 ¿Te fue útil esta respuesta?")
        
        col1, col2, col3 = st.columns([1, 1, 4])
        
        with col1:
            if st.button("✅ Sí, fue útil", key=f"util_{feedback_id}"):
                # Registrar feedback útil
                success = feedback_sistema.registrar_feedback(
                    consulta=consulta_original,
                    termino=termino_buscado,
                    util=True,
                    resultados_count=resultados_count,
                    respuesta=respuesta_generada
                )
                if success:
                    st.session_state[feedback_id] = True
                    st.success("✅ ¡Gracias por tu feedback! 🙌")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("Error al guardar feedback")
        
        with col2:
            if st.button("❌ No fue útil", key=f"no_util_{feedback_id}"):
                # Registrar feedback no útil primero
                success = feedback_sistema.registrar_feedback(
                    consulta=consulta_original,
                    termino=termino_buscado,
                    util=False,
                    resultados_count=resultados_count,
                    respuesta=respuesta_generada
                )
                
                if success:
                    st.session_state[feedback_id] = True
                    
                    # Mostrar opción de comentario adicional
                    with st.expander("💬 ¿Quieres darnos más detalles para mejorar?"):
                        comentario = st.text_area(
                            "¿Qué podría mejorar? ¿Qué información faltaba?",
                            placeholder="Ej: Faltaban libros más actuales, la respuesta no era precisa, etc.",
                            key=f"comentario_{feedback_id}"
                        )
                        
                        if st.button("📤 Enviar comentario", key=f"enviar_{feedback_id}"):
                            if comentario and comentario.strip():
                                feedback_sistema.guardar_comentario(
                                    consulta_original, 
                                    termino_buscado, 
                                    comentario
                                )
                                st.success("✅ ¡Comentario guardado! Muchas gracias.")
                                time.sleep(2)
                                st.rerun()
                            else:
                                st.warning("Por favor escribe un comentario antes de enviar.")
                    
                    st.info("Gracias por tu feedback. Lo usaremos para mejorar el sistema. 💡")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("Error al guardar feedback")
        
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.success("✅ Gracias por tu valoración. ¡Sigue consultando!")

# ==========================================
# PÁGINA DE MÉTRICAS
# ==========================================

def mostrar_pagina_metricas():
    """Muestra la página de métricas incluyendo feedback"""
    st.markdown("""
    <div style="text-align: center; margin: 20px 0;">
        <span style="font-size: 48px;">📊</span>
        <h1>Métricas del Sistema</h1>
        <p style="color: #888;">Análisis de uso y satisfacción</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Obtener métricas
    metricas_24h = metricas_sistema.obtener_metricas_ultimas_24h()
    feedback_metrics = feedback_sistema.obtener_metricas_feedback()
    
    # Métricas generales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        tasa_exito = 0
        if metricas_sistema.metricas['consultas_totales'] > 0:
            tasa_exito = (metricas_sistema.metricas['consultas_con_resultados'] / 
                         metricas_sistema.metricas['consultas_totales'] * 100)
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{metricas_sistema.metricas['consultas_totales']}</div>
            <div class="metric-label">Consultas Totales</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{metricas_24h['total_consultas']}</div>
            <div class="metric-label">Últimas 24h</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{tasa_exito:.1f}%</div>
            <div class="metric-label">Tasa de Éxito</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{len(metricas_sistema.metricas['sesiones'])}</div>
            <div class="metric-label">Sesiones Activas</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Métricas de feedback
    st.subheader("⭐ Métricas de Satisfacción")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{feedback_metrics['total']}</div>
            <div class="metric-label">Feedbacks Recibidos</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{feedback_metrics['tasa_efectividad']:.1f}%</div>
            <div class="metric-label">Tasa de Efectividad</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">✅ {feedback_metrics['util']} / ❌ {feedback_metrics['no_util']}</div>
            <div class="metric-label">Útil / No útil</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Términos más problemáticos y exitosos
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("⚠️ Términos con más feedback negativo")
        problematicos = feedback_metrics['terminos_problematicos']
        if problematicos:
            for termino, tasa, no_util, total in problematicos:
                st.write(f"• **{termino}**: {tasa:.0f}% negativo ({no_util}/{total})")
        else:
            st.info("No hay suficientes datos para mostrar")
    
    with col2:
        st.subheader("🌟 Términos con mejor feedback")
        exitosos = feedback_metrics['terminos_exitosos']
        if exitosos:
            for termino, tasa, util, total in exitosos:
                st.write(f"• **{termino}**: {tasa:.0f}% útil ({util}/{total})")
        else:
            st.info("No hay suficientes datos para mostrar")
    
    st.markdown("---")
    
    # Gráfico de evolución
    st.subheader("📈 Evolución de Consultas (Últimos 7 días)")
    
    ultimos_7_dias = []
    for i in range(7, 0, -1):
        fecha = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
        consultas = metricas_sistema.metricas['consultas_por_dia'].get(fecha, 0)
        ultimos_7_dias.append({'fecha': fecha, 'consultas': consultas})
    
    df_evolucion = pd.DataFrame(ultimos_7_dias)
    st.line_chart(df_evolucion.set_index('fecha'))
    
    st.markdown("---")
    
    # Países de acceso
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🌍 Países de Acceso")
        if metricas_sistema.metricas['paises_acceso']:
            for pais, cantidad in sorted(metricas_sistema.metricas['paises_acceso'].items(), 
                                        key=lambda x: x[1], reverse=True)[:10]:
                st.markdown(f'<span class="country-badge">📍 {pais}: {cantidad} consultas</span>', 
                           unsafe_allow_html=True)
        else:
            st.info("Aún no hay datos de ubicación disponibles")
    
    with col2:
        st.subheader("🔝 Términos Más Buscados")
        if metricas_sistema.metricas['terminos_buscados']:
            from collections import Counter
            terminos = [t['termino'] for t in metricas_sistema.metricas['terminos_buscados']]
            top_terminos = Counter(terminos).most_common(10)
            for termino, count in top_terminos:
                st.write(f"• **{termino}**: {count} veces")
        else:
            st.info("Aún no hay consultas registradas")
    
    st.markdown("---")
    
    # Últimos feedbacks
    st.subheader("🕐 Últimos Feedbacks")
    if feedback_sistema.feedback_data['ultimos_feedback']:
        for fb in reversed(feedback_sistema.feedback_data['ultimos_feedback'][-10:]):
            fecha = datetime.fromisoformat(fb['fecha']).strftime("%d/%m %H:%M")
            icono = "✅" if fb['util'] else "❌"
            st.markdown(f"{icono} **{fb['termino']}** - {fecha}")
    else:
        st.info("Aún no hay feedback registrado. ¡Sé el primero en dar feedback!")
    
    # Botones de exportación
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📥 Exportar Métricas (JSON)", key="export_metrics"):
            with open(metricas_sistema.archivo_metricas, 'r', encoding='utf-8') as f:
                json_data = f.read()
            st.download_button(
                label="Descargar métricas",
                data=json_data,
                file_name=f"metricas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                key="download_metrics"
            )
    
    with col2:
        if st.button("📊 Exportar Feedback (JSON)", key="export_feedback"):
            with open(feedback_sistema.archivo_feedback, 'r', encoding='utf-8') as f:
                json_data = f.read()
            st.download_button(
                label="Descargar feedback",
                data=json_data,
                file_name=f"feedback_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                key="download_feedback"
            )
    
    # Botón volver
    st.markdown("---")
    if st.button("🏠 Volver al Inicio"):
        st.session_state.pagina_actual = "inicio"
        st.rerun()

# ==========================================
# FUNCIONES PRINCIPALES DE BÚSQUEDA
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
    
    # Inicializar session state
    if 'pagina_actual' not in st.session_state:
        st.session_state.pagina_actual = "inicio"
    
    # Obtener información de sesión para métricas
    if 'session_id' not in st.session_state:
        st.session_state.session_id = str(int(time.time() * 1000))
    
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
        
        # Navegación
        st.markdown("### 🧭 Navegación")
        if st.button("📚 Inicio", use_container_width=True):
            st.session_state.pagina_actual = "inicio"
            st.rerun()
        
        if st.button("📊 Ver Métricas", use_container_width=True):
            st.session_state.pagina_actual = "metricas"
            st.rerun()
        
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
    
    # Mostrar página según selección
    if st.session_state.pagina_actual == "metricas":
        mostrar_pagina_metricas()
        mostrar_footer()
        return
    
    # Main content (página de inicio)
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
            
            # Registrar métrica
            ip_info = obtener_informacion_ip()
            metricas_sistema.registrar_consulta(
                termino=consulta,
                tuvo_resultados=len(resultados) > 0,
                session_id=st.session_state.session_id,
                ip_info=ip_info
            )
        
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
                
                # Mostrar botones de feedback
                mostrar_botones_feedback(
                    consulta_original=consulta,
                    termino_buscado=consulta,
                    resultados_count=len(resultados),
                    respuesta_generada=respuesta
                )
                
            else:
                st.warning(f"❌ No encontré libros sobre '{consulta}' en nuestro catálogo.")
                st.markdown("""
                💡 **Sugerencias:**
                - Revisa la ortografía
                - Prueba con palabras más generales
                - Busca por autor o tema
                """)
                
                # También mostrar feedback para búsquedas sin resultados
                respuesta_vacia = "No se encontraron libros en el catálogo para esta búsqueda."
                mostrar_botones_feedback(
                    consulta_original=consulta,
                    termino_buscado=consulta,
                    resultados_count=0,
                    respuesta_generada=respuesta_vacia
                )
    
    # Mostrar footer
    mostrar_footer()

if __name__ == "__main__":
    main()
