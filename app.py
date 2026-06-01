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
        graficos = {}
        
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
                graficos['impresiones_ubicacion'] = fig
        
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
                graficos['distribucion'] = fig
        
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
                graficos['gasto_ubicacion'] = fig
        
        # Gráfico 4: ROI (Resultados vs Gasto)
        with col_grafico4:
            if col_ubicacion and col_resultados and col_gasto:
                datos = df_filtrado.groupby(col_ubicacion).agg({
                    col_resultados: 'sum',
                    col_gasto: 'sum'
                }).reset_index()
                datos = datos[datos[col_gasto] > 0]  # Evitar división por cero
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
                graficos['roi'] = fig
        
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
            # Generar PDF con los gráficos
            try:
                from reportlab.lib.pagesizes import letter, landscape
                from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
                from reportlab.lib.units import inch
                from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle, Image
                from reportlab.lib import colors
                import tempfile
                import os
                
                def generar_pdf():
                    # Crear archivo temporal
                    pdf_file = io.BytesIO()
                    
                    # Crear documento PDF
                    doc = SimpleDocTemplate(pdf_file, pagesize=landscape(letter), topMargin=0.5*inch, bottomMargin=0.5*inch)
                    elements = []
                    
                    # Estilos
                    styles = getSampleStyleSheet()
                    title_style = ParagraphStyle(
                        'CustomTitle',
                        parent=styles['Heading1'],
                        fontSize=24,
                        textColor=colors.HexColor('#1f2937'),
                        spaceAfter=6,
                        alignment=1
                    )
                    
                    # Título
                    elements.append(Paragraph("📊 Reporte de Marketing", title_style))
                    elements.append(Paragraph(f"Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}", styles['Normal']))
                    elements.append(Spacer(1, 0.3*inch))
                    
                    # KPIs
                    elements.append(Paragraph("📈 Resumen de KPIs", styles['Heading2']))
                    kpi_data = [['Métrica', 'Valor']]
                    if kpi_alcance:
                        kpi_data.append(['Alcance', f"{int(kpi_alcance):,}"])
                    if kpi_impresiones:
                        kpi_data.append(['Impresiones', f"{int(kpi_impresiones):,}"])
                    if kpi_resultados:
                        kpi_data.append(['Resultados', f"{int(kpi_resultados)}"])
                    if kpi_clics:
                        kpi_data.append(['Clics', f"{int(kpi_clics)}"])
                    if kpi_ctr:
                        kpi_data.append(['CTR Promedio', f"{kpi_ctr:.2f}%"])
                    if kpi_gasto:
                        kpi_data.append(['Gasto Total', f"ARS {kpi_gasto:,.2f}"])
                    
                    table = Table(kpi_data)
                    table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3b82f6')),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, 0), 12),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black),
                        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f0f0')])
                    ]))
                    elements.append(table)
                    elements.append(Spacer(1, 0.3*inch))
                    
                    # Gráficos
                    elements.append(PageBreak())
                    elements.append(Paragraph("📊 Gráficos Detallados", styles['Heading2']))
                    elements.append(Spacer(1, 0.2*inch))
                    
                    # Convertir gráficos a imágenes PNG temporales
                    for nombre, fig in graficos.items():
                        try:
                            # Guardar gráfico como imagen PNG temporal
                            img_bytes = fig.to_image(format="png", width=900, height=500)
                            img = Image(io.BytesIO(img_bytes), width=7.5*inch, height=4.2*inch)
                            elements.append(img)
                            elements.append(Spacer(1, 0.3*inch))
                            
                            # Agregar salto de página después de cada 2 gráficos
                            if nombre != list(graficos.keys())[-1]:
                                elements.append(PageBreak())
                        except Exception as e:
                            st.warning(f"No se pudo incluir gráfico {nombre}")
                    
                    # Construir PDF
                    doc.build(elements)
                    pdf_file.seek(0)
                    return pdf_file
                
                pdf_buffer = generar_pdf()
                st.download_button(
                    label="📥 Descargar PDF",
                    data=pdf_buffer,
                    file_name=f"marketing_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                    mime="application/pdf"
                )
                
            except ImportError:
                st.warning("⚠️ Para descargar PDF, necesitas instalar reportlab. Usa: pip install reportlab")
            except Exception as e:
                st.error(f"❌ Error al generar PDF: {str(e)}")
        
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
    - ✅ **Descarga PDF directo** con los gráficos
    - ✅ Adaptable a cualquier estructura de datos
    
    ### 📋 Formato esperado:
    - Separador: `;` o `,`
    - Encoding: UTF-8 o Latin-1
    - Incluye columnas como: Ubicación, Impresiones, Alcance, Gasto, Resultados, CTR
    """)
