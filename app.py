import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import numpy as np

# Configurar página
st.set_page_config(
    page_title="Marketing Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos
st.markdown("""
    <style>
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
    }
    .metric-value {
        font-size: 32px;
        font-weight: bold;
        margin: 10px 0;
    }
    .metric-label {
        font-size: 14px;
        opacity: 0.9;
    }
    </style>
""", unsafe_allow_html=True)

# Título
st.title("📊 Marketing Dashboard")
st.markdown("*Visualización automática de datos de campañas - CSV adaptable*")

# Sidebar para carga de archivo
st.sidebar.header("⚙️ Configuración")
uploaded_file = st.sidebar.file_uploader("Sube tu archivo CSV", type=['csv'])

if uploaded_file is not None:
    try:
        # Detectar encoding y separador
        @st.cache_data
        def load_data(file):
            try:
                df = pd.read_csv(file, sep=';', encoding='latin-1')
            except:
                df = pd.read_csv(file, sep=',', encoding='utf-8')
            return df
        
        df = load_data(uploaded_file)
        
        # Función para detectar columnas automáticamente
        def encontrar_columna(df, palabras_clave):
            """Busca una columna que coincida con palabras clave"""
            df_cols = df.columns.tolist()
            for col in df_cols:
                col_lower = col.lower()
                for palabra in palabras_clave:
                    if palabra.lower() in col_lower:
                        return col
            return None
        
        # Mapeo de columnas disponibles
        col_ubicacion = encontrar_columna(df, ['ubicaci', 'placement', 'ubicacion'])
        col_impresiones = encontrar_columna(df, ['impresiones', 'impressions'])
        col_alcance = encontrar_columna(df, ['alcance', 'reach'])
        col_gasto = encontrar_columna(df, ['importe', 'gasto', 'spend', 'cost'])
        col_clics = encontrar_columna(df, ['clics', 'clicks'])
        col_resultados = encontrar_columna(df, ['resultado', 'conversion'])
        col_ctr = encontrar_columna(df, ['ctr', 'click-through'])
        col_campana = encontrar_columna(df, ['campana', 'campaign', 'nombre'])
        
        # Mostrar estado de detección
        with st.sidebar.expander("📋 Columnas detectadas"):
            cols_detectadas = {
                "Ubicación": col_ubicacion,
                "Impresiones": col_impresiones,
                "Alcance": col_alcance,
                "Gasto": col_gasto,
                "Clics": col_clics,
                "Resultados": col_resultados,
                "CTR": col_ctr,
                "Campaña": col_campana
            }
            for key, val in cols_detectadas.items():
                st.write(f"**{key}**: {val if val else '❌ No detectada'}")
        
        st.sidebar.success("✅ Archivo cargado exitosamente")
        
        # Limpiar datos
        df_clean = df.copy()
        
        # Convertir columnas numéricas
        numeric_cols = [col_impresiones, col_alcance, col_gasto, col_clics, col_resultados, col_ctr]
        for col in numeric_cols:
            if col and col in df_clean.columns:
                df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')
        
        # ===== SECCIÓN 1: KPIs PRINCIPALES =====
        st.markdown("## 📈 KPIs Principales")
        
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        
        with col1:
            if col_alcance:
                valor = df_clean[col_alcance].sum()
                st.metric("Alcance", f"{int(valor):,}")
        
        with col2:
            if col_impresiones:
                valor = df_clean[col_impresiones].sum()
                st.metric("Impresiones", f"{int(valor):,}")
        
        with col3:
            if col_resultados:
                valor = df_clean[col_resultados].sum()
                st.metric("Resultados", f"{int(valor)}")
        
        with col4:
            if col_clics:
                valor = df_clean[col_clics].sum()
                st.metric("Clics", f"{int(valor)}")
        
        with col5:
            if col_ctr:
                valor = df_clean[col_ctr].mean()
                st.metric("CTR Promedio", f"{valor:.2f}%")
        
        with col6:
            if col_gasto:
                valor = df_clean[col_gasto].sum()
                moneda = "ARS" if "ARS" in df.columns[0] else "$"
                st.metric("Gasto Total", f"{moneda} {valor:,.2f}")
        
        # ===== SECCIÓN 2: GRÁFICOS =====
        st.markdown("## 📊 Análisis Detallado")
        
        # Filtros
        col_filtro1, col_filtro2 = st.columns(2)
        
        with col_filtro1:
            if col_ubicacion:
                ubicaciones = st.multiselect(
                    "Filtrar por Ubicación:",
                    options=df_clean[col_ubicacion].unique(),
                    default=df_clean[col_ubicacion].unique()
                )
                df_filtrado = df_clean[df_clean[col_ubicacion].isin(ubicaciones)]
            else:
                df_filtrado = df_clean
        
        # Gráfico 1: Impresiones por ubicación
        col_grafico1, col_grafico2 = st.columns(2)
        
        with col_grafico1:
            if col_ubicacion and col_impresiones:
                datos = df_filtrado.groupby(col_ubicacion)[col_impresiones].sum().sort_values(ascending=False)
                fig = px.bar(
                    x=datos.index,
                    y=datos.values,
                    labels={'x': 'Ubicación', 'y': 'Impresiones'},
                    title="Impresiones por Ubicación",
                    color_discrete_sequence=['#3b82f6']
                )
                fig.update_layout(showlegend=False, height=400)
                st.plotly_chart(fig, use_container_width=True)
        
        # Gráfico 2: Distribución por ubicación (Pastel)
        with col_grafico2:
            if col_ubicacion and col_impresiones:
                datos = df_filtrado.groupby(col_ubicacion)[col_impresiones].sum()
                fig = px.pie(
                    values=datos.values,
                    names=datos.index,
                    title="Distribución de Impresiones",
                    color_discrete_sequence=px.colors.qualitative.Set3
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
        
        # Gráfico 3: Gasto por ubicación
        col_grafico3, col_grafico4 = st.columns(2)
        
        with col_grafico3:
            if col_ubicacion and col_gasto:
                datos = df_filtrado.groupby(col_ubicacion)[col_gasto].sum().sort_values(ascending=False)
                fig = px.bar(
                    x=datos.index,
                    y=datos.values,
                    labels={'x': 'Ubicación', 'y': 'Gasto'},
                    title="Gasto por Ubicación",
                    color_discrete_sequence=['#ef4444']
                )
                fig.update_layout(showlegend=False, height=400)
                st.plotly_chart(fig, use_container_width=True)
        
        # Gráfico 4: ROI (Resultados vs Gasto)
        with col_grafico4:
            if col_ubicacion and col_resultados and col_gasto:
                datos = df_filtrado.groupby(col_ubicacion).agg({
                    col_resultados: 'sum',
                    col_gasto: 'sum'
                }).reset_index()
                datos['ROI'] = (datos[col_resultados] / datos[col_gasto]).round(2)
                datos = datos.sort_values('ROI', ascending=False)
                
                fig = px.bar(
                    datos,
                    x=col_ubicacion,
                    y='ROI',
                    title="Resultados por Gasto (ROI)",
                    color_discrete_sequence=['#10b981']
                )
                fig.update_layout(showlegend=False, height=400)
                st.plotly_chart(fig, use_container_width=True)
        
        # ===== SECCIÓN 3: TABLA DETALLADA =====
        st.markdown("## 📋 Datos Detallados")
        
        # Seleccionar columnas para mostrar
        columnas_mostrar = [col for col in [col_ubicacion, col_campana, col_impresiones, col_alcance, 
                                            col_gasto, col_clics, col_resultados, col_ctr] 
                           if col is not None]
        
        if columnas_mostrar:
            df_mostrar = df_filtrado[columnas_mostrar].copy()
            
            # Formatear números
            for col in df_mostrar.columns:
                if df_mostrar[col].dtype in ['float64', 'int64']:
                    if col == col_gasto:
                        df_mostrar[col] = df_mostrar[col].apply(lambda x: f"${x:,.2f}" if pd.notna(x) else "N/A")
                    elif col == col_ctr:
                        df_mostrar[col] = df_mostrar[col].apply(lambda x: f"{x:.2f}%" if pd.notna(x) else "N/A")
                    else:
                        df_mostrar[col] = df_mostrar[col].apply(lambda x: f"{int(x):,}" if pd.notna(x) else "N/A")
            
            st.dataframe(df_mostrar, use_container_width=True, hide_index=True)
        
        # ===== SECCIÓN 4: DESCARGAS =====
        st.markdown("## 💾 Exportar Datos")
        
        col_desc1, col_desc2 = st.columns(2)
        
        with col_desc1:
            csv = df_filtrado.to_csv(index=False, sep=';', encoding='latin-1')
            st.download_button(
                label="📥 Descargar CSV filtrado",
                data=csv,
                file_name=f"marketing_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        
        with col_desc2:
            from io import BytesIO
            buffer = BytesIO()
            df_filtrado.to_excel(buffer, index=False)
            buffer.seek(0)
            st.download_button(
                label="📥 Descargar Excel",
                data=buffer,
                file_name=f"marketing_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        
        # Info del archivo
        st.sidebar.markdown("---")
        st.sidebar.info(f"""
        📁 **Información del archivo:**
        - Filas: {len(df_clean):,}
        - Columnas: {len(df_clean.columns)}
        - Tamaño: {uploaded_file.size / 1024:.2f} KB
        """)
    
    except Exception as e:
        st.error(f"❌ Error al procesar el archivo: {str(e)}")
        st.info("Asegúrate de que el archivo sea un CSV válido")

else:
    st.info("👉 Sube un archivo CSV en el panel izquierdo para comenzar")
    
    st.markdown("""
    ### 📚 Características:
    - ✅ Detección automática de columnas
    - ✅ Gráficos interactivos (Plotly)
    - ✅ Filtros dinámicos
    - ✅ Exportación a CSV y Excel
    - ✅ Adaptable a cualquier estructura de datos
    
    ### 📋 Formato esperado:
    - Separador: `;` o `,`
    - Encoding: UTF-8 o Latin-1
    - Incluye columnas como: Ubicación, Impresiones, Alcance, Gasto, etc.
    """)
