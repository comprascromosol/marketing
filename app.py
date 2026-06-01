import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import io

# Configurar página
st.set_page_config(
    page_title="Marketing Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

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
                try:
                    df = pd.read_csv(file, sep=',', encoding='utf-8')
                except:
                    df = pd.read_csv(file, sep=';', encoding='utf-8')
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
        col_resultados = encontrar_columna(df, ['resultado', 'conversion', 'conversaciones'])
        col_ctr = encontrar_columna(df, ['ctr', 'click-through'])
        col_campana = encontrar_columna(df, ['campana', 'campaign', 'nombre de la'])
        
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
        
        kpi_alcance = None
        kpi_impresiones = None
        kpi_resultados = None
        kpi_clics = None
        kpi_ctr = None
        kpi_gasto = None
        
        with col1:
            if col_alcance:
                kpi_alcance = df_clean[col_alcance].sum()
                st.metric("Alcance", f"{int(kpi_alcance):,}")
        
        with col2:
            if col_impresiones:
                kpi_impresiones = df_clean[col_impresiones].sum()
                st.metric("Impresiones", f"{int(kpi_impresiones):,}")
        
        with col3:
            if col_resultados:
                kpi_resultados = df_clean[col_resultados].sum()
                st.metric("Resultados", f"{int(kpi_resultados)}")
        
        with col4:
            if col_clics:
                kpi_clics = df_clean[col_clics].sum()
                st.metric("Clics", f"{int(kpi_clics)}")
        
        with col5:
            if col_ctr:
                kpi_ctr = df_clean[col_ctr].mean()
                st.metric("CTR Promedio", f"{kpi_ctr:.2f}%")
        
        with col6:
            if col_gasto:
                kpi_gasto = df_clean[col_gasto].sum()
                st.metric("Gasto Total", f"ARS {kpi_gasto:,.2f}")
        
        # ===== SECCIÓN 2: GRÁFICOS =====
        st.markdown("## 📊 Análisis Detallado")
        
        # Filtros
        if col_ubicacion:
            ubicaciones = st.multiselect(
                "Filtrar por Ubicación:",
                options=sorted(df_clean[col_ubicacion].dropna().unique()),
                default=sorted(df_clean[col_ubicacion].dropna().unique())
            )
            df_filtrado = df_clean[df_clean[col_ubicacion].isin(ubicaciones)]
        else:
            df_filtrado = df_clean
        
        # Almacenar gráficos para exportar
        graficos_html = {}
        
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
                fig.update_layout(showlegend=False, height=400, xaxis_tickangle=-45)
                st.plotly_chart(fig, use_container_width=True)
                graficos_html['impresiones_ubicacion'] = fig.to_html(include_plotlyjs='cdn')
        
        # Gráfico 2: Distribución por ubicación (Pastel)
        with col_grafico2:
            if col_ubicacion and col_impresiones:
                datos = df_filtrado.groupby(col_ubicacion)[col_impresiones].sum()
                fig = px.pie(
                    values=datos.values,
                    names=datos.index,
                    title="Distribución de Impresiones"
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
                graficos_html['distribucion'] = fig.to_html(include_plotlyjs='cdn')
        
        # Gráfico 3: Gasto por ubicación
        col_grafico3, col_grafico4 = st.columns(2)
        
        with col_grafico3:
            if col_ubicacion and col_gasto:
                datos = df_filtrado.groupby(col_ubicacion)[col_gasto].sum().sort_values(ascending=False)
                fig = px.bar(
                    x=datos.index,
                    y=datos.values,
                    labels={'x': 'Ubicación', 'y': 'Gasto (ARS)'},
                    title="Gasto por Ubicación",
                    color_discrete_sequence=['#ef4444']
                )
                fig.update_layout(showlegend=False, height=400, xaxis_tickangle=-45)
                st.plotly_chart(fig, use_container_width=True)
                graficos_html['gasto_ubicacion'] = fig.to_html(include_plotlyjs='cdn')
        
        # Gráfico 4: ROI (Resultados vs Gasto)
        with col_grafico4:
            if col_ubicacion and col_resultados and col_gasto:
                datos = df_filtrado.groupby(col_ubicacion).agg({
                    col_resultados: 'sum',
                    col_gasto: 'sum'
                }).reset_index()
                datos = datos[datos[col_gasto] > 0]
                datos['Costo por Resultado'] = (datos[col_gasto] / datos[col_resultados]).replace([float('inf'), -float('inf')], 0)
                datos = datos.sort_values('Costo por Resultado', ascending=True)
                
                fig = px.bar(
                    datos,
                    x=col_ubicacion,
                    y='Costo por Resultado',
                    title="Costo por Resultado (menor = mejor)",
                    color_discrete_sequence=['#10b981']
                )
                fig.update_layout(showlegend=False, height=400, xaxis_tickangle=-45)
                st.plotly_chart(fig, use_container_width=True)
                graficos_html['roi'] = fig.to_html(include_plotlyjs='cdn')
        
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
                        df_mostrar[col] = df_mostrar[col].apply(lambda x: f"ARS {x:,.2f}" if pd.notna(x) and x > 0 else "N/A")
                    elif col == col_ctr:
                        df_mostrar[col] = df_mostrar[col].apply(lambda x: f"{x:.2f}%" if pd.notna(x) else "N/A")
                    else:
                        df_mostrar[col] = df_mostrar[col].apply(lambda x: f"{int(x):,}" if pd.notna(x) and x > 0 else "N/A")
            
            st.dataframe(df_mostrar, use_container_width=True, hide_index=True)
        
        # ===== SECCIÓN 4: DESCARGAS =====
        st.markdown("## 💾 Exportar Datos")
        
        col_exp1, col_exp2 = st.columns(2)
        
        with col_exp1:
            csv = df_filtrado.to_csv(index=False, sep=';', encoding='latin-1')
            st.download_button(
                label="📥 Descargar CSV",
                data=csv,
                file_name=f"marketing_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        
        with col_exp2:
            # Generar HTML con los gráficos interactivos
            try:
                html_content = """
                <!DOCTYPE html>
                <html>
                <head>
                    <meta charset="utf-8">
                    <title>Reporte de Marketing</title>
                    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
                    <style>
                        * { margin: 0; padding: 0; box-sizing: border-box; }
                        body { 
                            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                            background: #f5f5f5;
                            padding: 20px;
                        }
                        .container { 
                            max-width: 1400px;
                            margin: 0 auto;
                            background: white;
                            padding: 30px;
                            border-radius: 8px;
                            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                        }
                        h1 { 
                            color: #1f2937;
                            text-align: center;
                            margin-bottom: 10px;
                            font-size: 32px;
                        }
                        .fecha { 
                            text-align: center;
                            color: #666;
                            margin-bottom: 30px;
                            font-size: 14px;
                        }
                        h2 { 
                            color: #1f2937;
                            margin-top: 30px;
                            margin-bottom: 20px;
                            border-bottom: 3px solid #3b82f6;
                            padding-bottom: 10px;
                            font-size: 20px;
                        }
                        .kpi-table {
                            width: 100%;
                            border-collapse: collapse;
                            margin-bottom: 30px;
                        }
                        .kpi-table th {
                            background: #3b82f6;
                            color: white;
                            padding: 12px;
                            text-align: left;
                            font-weight: 600;
                        }
                        .kpi-table td {
                            padding: 12px;
                            border-bottom: 1px solid #e5e7eb;
                        }
                        .kpi-table tr:nth-child(even) {
                            background: #f9fafb;
                        }
                        .graficos-grid {
                            display: grid;
                            grid-template-columns: 1fr 1fr;
                            gap: 30px;
                            margin: 30px 0;
                        }
                        .grafico-container {
                            background: #f9fafb;
                            padding: 20px;
                            border-radius: 8px;
                            border: 1px solid #e5e7eb;
                        }
                        .grafico-container > div {
                            width: 100%;
                        }
                        @media (max-width: 768px) {
                            .graficos-grid {
                                grid-template-columns: 1fr;
                            }
                        }
                        @media print {
                            body { background: white; }
                            .container { box-shadow: none; }
                            .grafico-container { page-break-inside: avoid; }
                        }
                    </style>
                </head>
                <body>
                    <div class="container">
                        <h1>📊 Reporte de Marketing</h1>
                        <div class="fecha">Generado: """ + datetime.now().strftime('%d/%m/%Y %H:%M') + """</div>
                        
                        <h2>📈 Resumen de KPIs</h2>
                        <table class="kpi-table">
                            <tr>
                                <th>Métrica</th>
                                <th>Valor</th>
                            </tr>
                """
                
                if kpi_alcance:
                    html_content += f"<tr><td>Alcance</td><td>{int(kpi_alcance):,}</td></tr>"
                if kpi_impresiones:
                    html_content += f"<tr><td>Impresiones</td><td>{int(kpi_impresiones):,}</td></tr>"
                if kpi_resultados:
                    html_content += f"<tr><td>Resultados</td><td>{int(kpi_resultados)}</td></tr>"
                if kpi_clics:
                    html_content += f"<tr><td>Clics</td><td>{int(kpi_clics)}</td></tr>"
                if kpi_ctr:
                    html_content += f"<tr><td>CTR Promedio</td><td>{kpi_ctr:.2f}%</td></tr>"
                if kpi_gasto:
                    html_content += f"<tr><td>Gasto Total</td><td>ARS {kpi_gasto:,.2f}</td></tr>"
                
                html_content += """
                        </table>
                        
                        <h2>📊 Gráficos Detallados</h2>
                        <div class="graficos-grid">
                """
                
                for nombre, grafico_html in graficos_html.items():
                    html_content += f'<div class="grafico-container">{grafico_html}</div>'
                
                html_content += """
                        </div>
                    </div>
                </body>
                </html>
                """
                
                st.download_button(
                    label="📥 Descargar Reporte (HTML)",
                    data=html_content,
                    file_name=f"marketing_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
                    mime="text/html"
                )
                
            except Exception as e:
                st.error(f"❌ Error al generar reporte: {str(e)}")
        
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
    - ✅ Exportación a CSV
    - ✅ Exportación a HTML (con gráficos interactivos)
    - ✅ Adaptable a cualquier estructura de datos
    
    ### 📋 Formato esperado:
    - Separador: `;` o `,`
    - Encoding: UTF-8 o Latin-1
    - Incluye columnas como: Ubicación, Impresiones, Alcance, Gasto, Resultados, CTR
    """)
