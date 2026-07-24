# Dashboard Climático del Departamento de Antioquia

Aplicación web profesional construida con **Python 3.12**, **Streamlit**, **Plotly** y **ArcGIS Maps SDK for JavaScript** para visualizar información climática de Antioquia, Colombia.

El proyecto incluye datos de ejemplo para desarrollo local y está preparado para conectar un WebMap o servicio publicado en ArcGIS Online mediante URL.

## Características

- Página principal con encabezado institucional, logo y KPIs.
- Barra lateral con filtros por fecha, subregión, municipio, variables climáticas y capas.
- Mapa ArcGIS interactivo con soporte para WebMap, Feature Layer y estaciones climáticas locales.
- Activación de capas de municipios, límites departamentales y estaciones.
- Tarjetas KPI para temperatura promedio, máxima, mínima, precipitación acumulada, estaciones y municipio con mayor precipitación.
- Gráficos Plotly: series temporales, precipitación, barras por municipio y mapa de calor.
- Tabla de consulta con nombre, temperatura, precipitación, altitud, coordenadas y población.
- Diseño claro, moderno, responsive e inspirado en ArcGIS Dashboards.
- Configuración lista para despliegue en Render.

## Estructura

```text
clima-antioquia-dashboard/
├── app.py
├── requirements.txt
├── README.md
├── Procfile
├── runtime.txt
├── assets/
│   ├── logo.png
│   └── style.css
├── data/
│   └── estaciones_climaticas_antioquia.csv
├── pages/
│   ├── mapa.py
│   ├── indicadores.py
│   └── estadisticas.py
└── utils/
    └── helpers.py
```

## Instalación

```bash
cd clima-antioquia-dashboard
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

En macOS o Linux:

```bash
source .venv/bin/activate
```

## Cómo ejecutar

```bash
streamlit run app.py
```

Luego abra la URL local que entrega Streamlit, normalmente:

```text
http://localhost:8501
```

## Conectar ArcGIS Online

En la barra lateral, pegue la URL de un WebMap o servicio de ArcGIS Online.

Ejemplos válidos:

```text
https://www.arcgis.com/home/item.html?id=ID_DEL_WEBMAP
https://services.arcgis.com/.../arcgis/rest/services/.../FeatureServer/0
```

Para mejores resultados, las capas climáticas deben exponer campos equivalentes o adaptables a:

- `municipio`
- `temperatura_c`
- `precipitacion_mm`
- `altitud_m`
- `poblacion`

## Datos

El archivo `data/estaciones_climaticas_antioquia.csv` contiene datos sintéticos de estaciones meteorológicas para pruebas. Para producción, reemplace este archivo por datos oficiales o conecte las capas publicadas desde ArcGIS Online.

## Capturas esperadas

- Vista inicial con título, logo, filtros laterales y tarjetas KPI.
- Página de mapa con estaciones sobre Antioquia y control de capas ArcGIS.
- Página de indicadores con tabla comparativa municipal.
- Página de estadísticas con series temporales, barras y mapa de calor.

## Despliegue en Render

1. Suba el proyecto a GitHub.
2. Cree un nuevo **Web Service** en Render.
3. Seleccione el repositorio.
4. Configure:

```text
Build Command: pip install -r requirements.txt
Start Command: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
```

El `Procfile` ya incluye el comando de arranque para Render.

## Dependencias principales

- Streamlit
- Pandas
- Plotly
- NumPy
- python-dotenv
- ArcGIS Maps SDK for JavaScript mediante CDN

## Buenas prácticas incluidas

- Separación de lógica en `utils/helpers.py`.
- Páginas multipage de Streamlit.
- Componentes visuales reutilizables.
- Caché de lectura de datos.
- Configuración de tema Streamlit.
- Datos locales reemplazables.
- Preparación para despliegue cloud.

## Licencia

MIT. Puede adaptar este proyecto para uso académico, institucional o comercial conservando la atribución correspondiente.
