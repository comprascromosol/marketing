# 📊 Marketing Dashboard

Dashboard interactivo para visualizar y analizar datos de campañas de marketing desde archivos CSV. Detecta automáticamente las columnas de tu archivo y genera gráficos, KPIs y reportes.

## 🚀 Características

✅ **Detección automática de columnas** - Se adapta a cualquier estructura de CSV
✅ **Gráficos interactivos** - Visualizaciones con Plotly
✅ **KPIs en tiempo real** - Alcance, impresiones, resultados, clics, CTR, gasto
✅ **Filtros dinámicos** - Filtra por ubicación y otras dimensiones
✅ **Exportación de datos** - Descarga CSV y Excel
✅ **Soporte multi-idioma** - Lee archivos con diferentes encodings

## 📋 Requisitos

- Python 3.8+
- pip

## 🔧 Instalación

```bash
# Clonar el repositorio
git clone https://github.com/comprascromosol/marketing.git
cd marketing

# Instalar dependencias
pip install -r requirements.txt
```

## ▶️ Ejecución

```bash
streamlit run app.py
```

La aplicación se abrirá en tu navegador en `http://localhost:8501`

## 📁 Formato de archivo

El CSV debe tener el siguiente formato:

- **Separador**: `;` o `,`
- **Encoding**: UTF-8 o Latin-1
- **Columnas sugeridas**:
  - Ubicación / Placement
  - Impresiones / Impressions
  - Alcance / Reach
  - Gasto / Spend / Importe gastado
  - Clics / Clicks
  - Resultados / Conversions
  - CTR / Click-through rate

### Ejemplo de estructura:

```
Nombre de la campaña;Anuncios;Ubicación;Alcance;Importe gastado (ARS);Impresiones;Resultados;Clics en el enlace;CTR (todos)
Nueva campaña;Anuncio 1;Feed;4730;24876.71;7357;14;36;1.82
```

## 📊 Vistas disponibles

### 1. KPIs Principales
- Alcance
- Impresiones
- Resultados
- Clics
- CTR Promedio
- Gasto Total

### 2. Gráficos
- **Impresiones por ubicación** - Gráfico de barras
- **Distribución de impresiones** - Gráfico de pastel
- **Gasto por ubicación** - Gráfico de barras
- **ROI (Resultados/Gasto)** - Análisis de eficiencia

### 3. Tabla Detallada
- Vista completa de los datos con formato automático

### 4. Exportación
- Descarga CSV filtrado
- Descarga Excel

## 🎨 Personalización

El dashboard detecta automáticamente:
- Ubicaciones / Placements
- Métricas de impresiones
- Métricas de alcance
- Datos de gasto
- Clics y resultados
- Tasas de conversión

No requiere configuración manual, ¡solo sube tu CSV!

## 🐛 Solución de problemas

**El archivo no se procesa:**
- Asegúrate de que sea CSV (no XLSX)
- Verifica el separador (`;` o `,`)
- Comprueba el encoding del archivo

**Las columnas no se detectan:**
- Revisa los nombres de las columnas
- El sistema busca palabras clave (ubicación, impresiones, etc.)
- Agrega nombres estándar a tus columnas si es posible

## 📝 Licencia

MIT

## 👤 Autor

comprascromosol

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor abre un issue o pull request.
