import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import io
from itertools import combinations

# Configurar página
st.set_page_config(
    page_title="Universal Data Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Título
st.title("📊 Universal Data Dashboard")
st.markdown("*Visualización automática y adaptable a cualquier tipo de datos - CSV flexible*")

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
        
        st.sidebar.success("✅ Archivo cargado exitosamente")
        
        # ===== ANÁLISIS DE COLUMNAS =====
        
        # Identificar tipos de columnas
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
        datetime_cols = df.select_dtypes(include=['datetime64']).columns.tolist()
        
        # Información del archivo
        st.sidebar.markdown("---")
        with st.sidebar.expander("📋 Información del Archivo"):
            st.write(f"**Filas:** {len(df):,}")
            st.write(f"**Columnas:** {len(df.columns)}")
            st.write(f"**Tamaño:** {uploaded_file.size / 1024:.2f} KB")
            st.write(f"\n**Columnas Numéricas:** {len(numeric_cols)}")
            for col in numeric_cols[:5]:
                st.write(f"  • {col}")
            if len(numeric_cols) > 5:
                st.write(f"  • ... y {len(numeric_cols) - 5} más")
            st.write(f"\n**Columnas Categóricas:** {len(categorical_cols)}")
            for col in categorical_cols[:5]:
                st.write(f"  • {col}")
            if len(categorical_cols) > 5:
                st.write(f"  • ... y {len(categorical_cols) - 5} más")
        
        # ===== SECCIÓN 1: ESTADÍSTICAS GENERALES =====
        st.markdown("## 📊 Estadísticas Generales")
        
        if numeric_cols:
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total de Filas", f"{len(df):,}")
            
            with col2:
                st.metric("Columnas Numéricas", len(numeric_cols))
            
            with col3:
                st.metric("Columnas Categóricas", len(categorical_cols))
            
            with col4:
                st.metric("Valores Nulos", df.isnull().sum().sum())
            
            # Tabla de estadísticas
            st.markdown("### Resumen Estadístico")
            st.dataframe(df[numeric_cols].describe().round(2), use_container_width=True)
        
        # ===== SECCIÓN 2: GRÁFICOS INTELIGENTES =====
        st.markdown("## 📈 Generador de Gráficos")
        
        graficos_html = {}
        graficos_figs = {}
        graficos_info = []
        
        # Gráficos automáticos por columnas numéricas
        if numeric_cols:
            st.markdown("### 📊 Análisis de Columnas Numéricas")
            
            # Top columnas por varianza
            numeric_df = df[numeric_cols].copy()
            numeric_df = numeric_df.dropna()
            
            if len(numeric_df) > 0:
                # Gráfico 1: Distribución de la primera columna numérica
                col1, col2 = st.columns(2)
                
                with col1:
                    if len(numeric_cols) >= 1:
                        col_selected = numeric_cols[0]
                        fig = px.histogram(
                            df,
                            x=col_selected,
                            nbins=30,
                            title=f"Distribución de {col_selected}",
                            color_discrete_sequence=['#3b82f6']
                        )
                        fig.update_layout(height=400, showlegend=False)
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Botón para descargar PDF
                        st.download_button(
                            label=f"📥 Descargar {col_selected} (PDF)",
                            data=fig.to_image(format="pdf", width=1000, height=600),
                            file_name=f"grafico_distribucion_{col_selected}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                            mime="application/pdf"
                        )
                        
                        graficos_html[f'distribucion_{col_selected}'] = fig.to_html(include_plotlyjs='cdn')
                        graficos_figs[f'distribucion_{col_selected}'] = fig
                        graficos_info.append(f"Distribución de {col_selected}")
                
                with col2:
                    if len(numeric_cols) >= 2:
                        # Gráfico 2: Correlación de dos primeras columnas
                        col_x = numeric_cols[0]
                        col_y = numeric_cols[1]
                        
                        fig = px.scatter(
                            df,
                            x=col_x,
                            y=col_y,
                            title=f"{col_x} vs {col_y}",
                            color_discrete_sequence=['#ef4444']
                        )
                        fig.update_layout(height=400)
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Botón para descargar PDF
                        st.download_button(
                            label=f"📥 Descargar Scatter (PDF)",
                            data=fig.to_image(format="pdf", width=1000, height=600),
                            file_name=f"grafico_scatter_{col_x}_{col_y}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                            mime="application/pdf"
                        )
                        
                        graficos_html[f'scatter_{col_x}_{col_y}'] = fig.to_html(include_plotlyjs='cdn')
                        graficos_figs[f'scatter_{col_x}_{col_y}'] = fig
                        graficos_info.append(f"Scatter: {col_x} vs {col_y}")
        
        # Gráficos para columnas categóricas
        if categorical_cols and numeric_cols:
            st.markdown("### 🎯 Análisis por Categorías")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if len(categorical_cols) >= 1 and len(numeric_cols) >= 1:
                    cat_col = categorical_cols[0]
                    num_col = numeric_cols[0]
                    
                    # Agrupar y sumar
                    datos = df.groupby(cat_col)[num_col].sum().sort_values(ascending=False).head(10)
                    
                    fig = px.bar(
                        x=datos.index,
                        y=datos.values,
                        labels={'x': cat_col, 'y': num_col},
                        title=f"{num_col} por {cat_col}",
                        color_discrete_sequence=['#10b981']
                    )
                    fig.update_layout(height=400, xaxis_tickangle=-45, showlegend=False)
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Botón para descargar PDF
                    st.download_button(
                        label=f"📥 Descargar Barras (PDF)",
                        data=fig.to_image(format="pdf", width=1000, height=600),
                        file_name=f"grafico_barras_{cat_col}_{num_col}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                        mime="application/pdf"
                    )
                    
                    graficos_html[f'bar_{cat_col}_{num_col}'] = fig.to_html(include_plotlyjs='cdn')
                    graficos_figs[f'bar_{cat_col}_{num_col}'] = fig
                    graficos_info.append(f"Barras: {num_col} por {cat_col}")
            
            with col2:
                if len(categorical_cols) >= 1 and len(numeric_cols) >= 1:
                    cat_col = categorical_cols[0]
                    num_col = numeric_cols[0]
                    
                    # Gráfico de pie
                    datos = df.groupby(cat_col)[num_col].sum().head(10)
                    
                    fig = px.pie(
                        values=datos.values,
                        names=datos.index,
                        title=f"Distribución de {num_col} por {cat_col}"
                    )
                    fig.update_layout(height=400)
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Botón para descargar PDF
                    st.download_button(
                        label=f"📥 Descargar Pie (PDF)",
                        data=fig.to_image(format="pdf", width=1000, height=600),
                        file_name=f"grafico_pie_{cat_col}_{num_col}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                        mime="application/pdf"
                    )
                    
                    graficos_html[f'pie_{cat_col}_{num_col}'] = fig.to_html(include_plotlyjs='cdn')
                    graficos_figs[f'pie_{cat_col}_{num_col}'] = fig
                    graficos_info.append(f"Pie: {num_col} por {cat_col}")
        
        # Gráfico de línea temporal si hay series
        if len(numeric_cols) >= 2:
            st.markdown("### 📈 Análisis Multi-variable")
            
            # Seleccionar columnas para gráfico de línea
            col_x_select = st.selectbox("Selecciona columna para eje X:", numeric_cols, key="line_x")
            col_y_select = st.multiselect("Selecciona columnas para eje Y:", 
                                          [c for c in numeric_cols if c != col_x_select],
                                          default=[numeric_cols[1]] if len(numeric_cols) > 1 else [])
            
            if col_y_select:
                # Crear gráfico de líneas
                df_sorted = df.sort_values(col_x_select)
                
                fig = go.Figure()
                colors = ['#3b82f6', '#ef4444', '#10b981', '#f59e0b', '#8b5cf6']
                
                for idx, col_y in enumerate(col_y_select):
                    fig.add_trace(go.Scatter(
                        x=df_sorted[col_x_select],
                        y=df_sorted[col_y],
                        mode='lines+markers',
                        name=col_y,
                        line=dict(color=colors[idx % len(colors)], width=2),
                        marker=dict(size=6)
                    ))
                
                fig.update_layout(
                    title=f"{col_x_select} vs {', '.join(col_y_select)}",
                    xaxis_title=col_x_select,
                    yaxis_title="Valores",
                    height=450,
                    hovermode='x unified'
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Botón para descargar PDF
                st.download_button(
                    label=f"📥 Descargar Línea (PDF)",
                    data=fig.to_image(format="pdf", width=1200, height=700),
                    file_name=f"grafico_linea_{col_x_select}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                    mime="application/pdf"
                )
                
                graficos_html[f'linea_{col_x_select}'] = fig.to_html(include_plotlyjs='cdn')
                graficos_figs[f'linea_{col_x_select}'] = fig
                graficos_info.append(f"Línea: {col_x_select} vs {', '.join(col_y_select)}")
        
        # ===== SECCIÓN 3: TABLA DETALLADA =====
        st.markdown("## 📋 Datos Detallados")
        
        # Opciones de filtrado
        col_filter1, col_filter2 = st.columns(2)
        
        with col_filter1:
            if categorical_cols:
                selected_category = st.selectbox(
                    "Filtrar por categoría:",
                    ["Todos"] + categorical_cols,
                    key="filter_cat"
                )
        
        with col_filter2:
            if categorical_cols and selected_category != "Todos":
                unique_values = df[selected_category].unique()
                selected_value = st.selectbox(
                    f"Valores de {selected_category}:",
                    unique_values,
                    key="filter_val"
                )
        
        # Aplicar filtro
        if categorical_cols and selected_category != "Todos":
            df_filtered = df[df[selected_category] == selected_value]
        else:
            df_filtered = df
        
        # Mostrar tabla
        st.dataframe(df_filtered, use_container_width=True, height=400)
        
        # ===== SECCIÓN 4: DESCARGAS =====
        st.markdown("## 💾 Exportar Datos")
        
        col_exp1, col_exp2, col_exp3 = st.columns(3)
        
        with col_exp1:
            csv = df_filtered.to_csv(index=False, sep=';', encoding='latin-1')
            st.download_button(
                label="📥 Descargar CSV Filtrado",
                data=csv,
                file_name=f"data_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        
        with col_exp2:
            # Descargar todos los gráficos en un ZIP
            try:
                import zipfile
                
                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                    for nombre, fig in graficos_figs.items():
                        try:
                            pdf_data = fig.to_image(format="pdf", width=1000, height=600)
                            zip_file.writestr(
                                f"grafico_{nombre}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                                pdf_data
                            )
                        except:
                            pass
                
                zip_buffer.seek(0)
                st.download_button(
                    label="📥 Descargar Todos los PDFs (ZIP)",
                    data=zip_buffer,
                    file_name=f"graficos_completo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
                    mime="application/zip"
                )
            except Exception as e:
                st.info("⚠️ Para descargar PDFs, se necesita kaleido")
        
        with col_exp3:
            # Generar HTML con reportes
            try:
                html_content = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <meta charset="utf-8">
                    <title>Reporte de Datos</title>
                    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
                    <style>
                        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
                        body {{ 
                            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                            background: #f5f5f5;
                            padding: 20px;
                        }}
                        .container {{ 
                            max-width: 1400px;
                            margin: 0 auto;
                            background: white;
                            padding: 30px;
                            border-radius: 8px;
                            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                        }}
                        h1 {{ 
                            color: #1f2937;
                            text-align: center;
                            margin-bottom: 10px;
                            font-size: 32px;
                        }}
                        .fecha {{ 
                            text-align: center;
                            color: #666;
                            margin-bottom: 30px;
                            font-size: 14px;
                        }}
                        h2 {{ 
                            color: #1f2937;
                            margin-top: 30px;
                            margin-bottom: 20px;
                            border-bottom: 3px solid #3b82f6;
                            padding-bottom: 10px;
                            font-size: 20px;
                        }}
                        .stats-grid {{
                            display: grid;
                            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                            gap: 20px;
                            margin-bottom: 30px;
                        }}
                        .stat-card {{
                            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                            color: white;
                            padding: 20px;
                            border-radius: 8px;
                            text-align: center;
                        }}
                        .stat-value {{
                            font-size: 28px;
                            font-weight: bold;
                            margin: 10px 0;
                        }}
                        .stat-label {{
                            font-size: 12px;
                            opacity: 0.9;
                        }}
                        .graficos-grid {{
                            display: grid;
                            grid-template-columns: 1fr;
                            gap: 30px;
                            margin: 30px 0;
                        }}
                        .grafico-container {{
                            background: #f9fafb;
                            padding: 20px;
                            border-radius: 8px;
                            border: 1px solid #e5e7eb;
                            page-break-inside: avoid;
                        }}
                        .grafico-container > div {{
                            width: 100%;
                        }}
                        @media print {{
                            body {{ background: white; }}
                            .container {{ box-shadow: none; }}
                            .grafico-container {{ page-break-inside: avoid; }}
                        }}
                    </style>
                </head>
                <body>
                    <div class="container">
                        <h1>📊 Reporte de Datos</h1>
                        <div class="fecha">Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}</div>
                        
                        <h2>📈 Estadísticas Generales</h2>
                        <div class="stats-grid">
                            <div class="stat-card">
                                <div class="stat-label">Total de Filas</div>
                                <div class="stat-value">{len(df):,}</div>
                            </div>
                            <div class="stat-card">
                                <div class="stat-label">Columnas Numéricas</div>
                                <div class="stat-value">{len(numeric_cols)}</div>
                            </div>
                            <div class="stat-card">
                                <div class="stat-label">Columnas Categóricas</div>
                                <div class="stat-value">{len(categorical_cols)}</div>
                            </div>
                            <div class="stat-card">
                                <div class="stat-label">Valores Nulos</div>
                                <div class="stat-value">{df.isnull().sum().sum()}</div>
                            </div>
                        </div>
                        
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
                    file_name=f"data_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
                    mime="text/html"
                )
                
            except Exception as e:
                st.error(f"❌ Error al generar reporte: {str(e)}")
    
    except Exception as e:
        st.error(f"❌ Error al procesar el archivo: {str(e)}")
        st.info("Asegúrate de que el archivo sea un CSV válido")

else:
    st.info("👉 Sube un archivo CSV en el panel izquierdo para comenzar")
    
    st.markdown("""
    ### 📚 Características:
    - ✅ **Adaptación automática** a cualquier tipo de datos
    - ✅ Detección inteligente de columnas numéricas y categóricas
    - ✅ Gráficos dinámicos e interactivos (Plotly)
    - ✅ **Descarga individual de gráficos en PDF**
    - ✅ **Descarga todos los gráficos en ZIP**
    - ✅ Filtros personalizables
    - ✅ Estadísticas automáticas
    - ✅ Exportación a CSV e HTML
    - ✅ Reportes profesionales con estilos
    
    ### 📋 Formatos soportados:
    - Separadores: `;` o `,`
    - Encoding: UTF-8 o Latin-1
    - Cualquier estructura de datos (ventas, analytics, finanzas, etc.)
    
    ### 🎯 Casos de uso:
    - 📊 Dashboard de marketing y publicidad
    - 💰 Análisis de ventas y finanzas
    - 📈 Reportes de desempeño
    - 🎯 Métricas de negocio
    - 📉 Análisis de datos exploratorio
    """)
