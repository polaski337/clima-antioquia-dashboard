from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT_DIR / "data" / "estaciones_climaticas_antioquia.csv"
STYLE_PATH = ROOT_DIR / "assets" / "style.css"
LOGO_PATH = ROOT_DIR / "assets" / "logo.png"

VARIABLES = {
    "Temperatura": {
        "column": "temperatura_c",
        "unit": "°C",
        "color": "#de3b32",
    },
    "Precipitación": {
        "column": "precipitacion_mm",
        "unit": "mm",
        "color": "#0079c1",
    },
    "Humedad relativa": {
        "column": "humedad_relativa",
        "unit": "%",
        "color": "#2b9c8f",
    },
    "Velocidad del viento": {
        "column": "velocidad_viento_kmh",
        "unit": "km/h",
        "color": "#7a5af8",
    },
    "Radiación solar": {
        "column": "radiacion_solar_wm2",
        "unit": "W/m²",
        "color": "#f3c613",
    },
}


@dataclass(frozen=True)
class FilterState:
    start_date: pd.Timestamp
    end_date: pd.Timestamp
    subregions: list[str]
    municipios: list[str]
    variables: list[str]
    arcgis_url: str
    show_municipios: bool
    show_limites: bool
    show_estaciones: bool


def configure_page(title: str = "Dashboard Climático de Antioquia") -> None:
    st.set_page_config(
        page_title=title,
        page_icon="🌦️",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    load_css()


def load_css() -> None:
    if STYLE_PATH.exists():
        st.markdown(f"<style>{STYLE_PATH.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)


@st.cache_data(show_spinner=False)
def load_climate_data(path: str | Path = DATA_PATH) -> pd.DataFrame:
    df = pd.read_csv(path)
    df["fecha"] = pd.to_datetime(df["fecha"])
    numeric_columns = [
        "latitud",
        "longitud",
        "altitud_m",
        "poblacion",
        "temperatura_c",
        "precipitacion_mm",
        "humedad_relativa",
        "velocidad_viento_kmh",
        "radiacion_solar_wm2",
    ]
    for column in numeric_columns:
        df[column] = pd.to_numeric(df[column], errors="coerce")
    return df


def render_header() -> None:
    st.markdown(
        f"""
        <div class="hero">
          <img class="hero-logo" src="data:image/png;base64,{logo_base64()}" alt="Logo">
          <div>
            <h1>Dashboard Climático del Departamento de Antioquia</h1>
            <p>Monitoreo territorial de variables climáticas, estaciones y municipios para análisis operativo.</p>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


@st.cache_data(show_spinner=False)
def logo_base64() -> str:
    import base64

    if not LOGO_PATH.exists():
        return ""
    return base64.b64encode(LOGO_PATH.read_bytes()).decode("utf-8")


def sidebar_filters(df: pd.DataFrame) -> FilterState:
    st.sidebar.image(str(LOGO_PATH), width=96)
    st.sidebar.title("Filtros")

    min_date = df["fecha"].min().date()
    max_date = df["fecha"].max().date()
    date_range = st.sidebar.date_input(
        "Rango de fechas",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )
    if len(date_range) != 2:
        start_date, end_date = min_date, max_date
    else:
        start_date, end_date = date_range

    subregions = st.sidebar.multiselect(
        "Subregiones",
        options=sorted(df["subregion"].dropna().unique()),
        default=sorted(df["subregion"].dropna().unique()),
    )
    available = df[df["subregion"].isin(subregions)] if subregions else df
    municipios = st.sidebar.multiselect(
        "Municipios",
        options=sorted(available["municipio"].dropna().unique()),
        default=sorted(available["municipio"].dropna().unique()),
    )
    variables = st.sidebar.multiselect(
        "Variables climáticas",
        options=list(VARIABLES.keys()),
        default=["Temperatura", "Precipitación", "Humedad relativa"],
    )

    st.sidebar.divider()
    st.sidebar.subheader("ArcGIS Online")
    arcgis_url = st.sidebar.text_input(
        "URL del WebMap o servicio",
        value="",
        placeholder="https://www.arcgis.com/home/item.html?id=...",
    )
    show_municipios = st.sidebar.checkbox("Municipios", value=True)
    show_limites = st.sidebar.checkbox("Límites departamentales", value=True)
    show_estaciones = st.sidebar.checkbox("Estaciones meteorológicas", value=True)

    return FilterState(
        start_date=pd.Timestamp(start_date),
        end_date=pd.Timestamp(end_date),
        subregions=subregions,
        municipios=municipios,
        variables=variables,
        arcgis_url=arcgis_url.strip(),
        show_municipios=show_municipios,
        show_limites=show_limites,
        show_estaciones=show_estaciones,
    )


def apply_filters(df: pd.DataFrame, filters: FilterState) -> pd.DataFrame:
    mask = df["fecha"].between(filters.start_date, filters.end_date)
    if filters.subregions:
        mask &= df["subregion"].isin(filters.subregions)
    if filters.municipios:
        mask &= df["municipio"].isin(filters.municipios)
    return df.loc[mask].copy()


def calculate_kpis(df: pd.DataFrame) -> dict[str, str]:
    if df.empty:
        return {
            "Temperatura promedio": "Sin datos",
            "Temperatura máxima": "Sin datos",
            "Temperatura mínima": "Sin datos",
            "Precipitación acumulada": "Sin datos",
            "Número de estaciones": "0",
            "Municipio con mayor precipitación": "Sin datos",
        }

    precip_by_municipio = df.groupby("municipio", as_index=False)["precipitacion_mm"].sum()
    top_precip = precip_by_municipio.sort_values("precipitacion_mm", ascending=False).iloc[0]

    return {
        "Temperatura promedio": f"{df['temperatura_c'].mean():.1f} °C",
        "Temperatura máxima": f"{df['temperatura_c'].max():.1f} °C",
        "Temperatura mínima": f"{df['temperatura_c'].min():.1f} °C",
        "Precipitación acumulada": f"{df['precipitacion_mm'].sum():,.1f} mm",
        "Número de estaciones": f"{df['estacion'].nunique():,}",
        "Municipio con mayor precipitación": f"{top_precip['municipio']} ({top_precip['precipitacion_mm']:.1f} mm)",
    }


def render_kpi_cards(df: pd.DataFrame) -> None:
    kpis = calculate_kpis(df)
    cols = st.columns(3)
    for index, (label, value) in enumerate(kpis.items()):
        with cols[index % 3]:
            st.markdown(
                f"""
                <div class="kpi-card">
                  <div class="kpi-label">{label}</div>
                  <div class="kpi-value">{value}</div>
                  <div class="kpi-subtitle">Periodo filtrado</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def line_chart(df: pd.DataFrame, variable_name: str) -> go.Figure:
    meta = VARIABLES[variable_name]
    grouped = df.groupby("fecha", as_index=False)[meta["column"]].mean()
    fig = px.line(
        grouped,
        x="fecha",
        y=meta["column"],
        markers=True,
        labels={"fecha": "Fecha", meta["column"]: f"{variable_name} ({meta['unit']})"},
        color_discrete_sequence=[meta["color"]],
    )
    return polish_figure(fig)


def precipitation_chart(df: pd.DataFrame) -> go.Figure:
    grouped = df.groupby("fecha", as_index=False)["precipitacion_mm"].sum()
    fig = px.bar(
        grouped,
        x="fecha",
        y="precipitacion_mm",
        labels={"fecha": "Fecha", "precipitacion_mm": "Precipitación acumulada (mm)"},
        color_discrete_sequence=["#0079c1"],
    )
    return polish_figure(fig)


def municipality_bar_chart(df: pd.DataFrame, variable_name: str) -> go.Figure:
    meta = VARIABLES[variable_name]
    agg = "sum" if meta["column"] == "precipitacion_mm" else "mean"
    grouped = getattr(df.groupby("municipio", as_index=False)[meta["column"]], agg)()
    grouped = grouped.sort_values(meta["column"], ascending=False)
    fig = px.bar(
        grouped,
        x=meta["column"],
        y="municipio",
        orientation="h",
        labels={"municipio": "Municipio", meta["column"]: f"{variable_name} ({meta['unit']})"},
        color=meta["column"],
        color_continuous_scale="Bluered",
    )
    fig.update_layout(yaxis={"categoryorder": "total ascending"}, coloraxis_showscale=False)
    return polish_figure(fig)


def heatmap_chart(df: pd.DataFrame, variable_name: str) -> go.Figure:
    meta = VARIABLES[variable_name]
    pivot = (
        df.assign(mes=df["fecha"].dt.strftime("%Y-%m"))
        .pivot_table(index="municipio", columns="mes", values=meta["column"], aggfunc="mean")
        .sort_index()
    )
    fig = px.imshow(
        pivot,
        aspect="auto",
        color_continuous_scale="RdYlBu_r",
        labels={"x": "Mes", "y": "Municipio", "color": f"{variable_name} ({meta['unit']})"},
    )
    fig.update_coloraxes(
        colorbar=dict(
            title=dict(font=dict(color="#0f172a", size=13)),
            tickfont=dict(color="#0f172a", size=12),
        )
    )
    return polish_figure(fig)


def polish_figure(fig: go.Figure) -> go.Figure:
    fig.update_layout(
        template="plotly_white",
        margin=dict(l=10, r=10, t=24, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#ffffff",
        font=dict(color="#0f172a", size=13),
        hovermode="x unified",
        height=390,
    )
    axis_style = dict(
        showgrid=True,
        gridcolor="#edf2f7",
        linecolor="#cbd5e1",
        tickfont=dict(color="#0f172a", size=12),
        title_font=dict(color="#0f172a", size=13),
    )
    fig.update_xaxes(**axis_style)
    fig.update_yaxes(**axis_style)
    fig.update_layout(
        legend=dict(font=dict(color="#0f172a")),
        hoverlabel=dict(bgcolor="#ffffff", font_color="#0f172a", bordercolor="#cbd5e1"),
    )
    return fig


def plotly_config() -> dict[str, bool]:
    return {
        "displayModeBar": False,
        "responsive": True,
    }


def latest_station_snapshot(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    latest_date = df["fecha"].max()
    return df[df["fecha"].eq(latest_date)].copy()


def parse_arcgis_item_id(url: str) -> str:
    if not url:
        return ""
    parsed = urlparse(url)
    query_id = parse_qs(parsed.query).get("id", [""])[0]
    if query_id:
        return query_id
    parts = [part for part in parsed.path.split("/") if part]
    if "items" in parts:
        index = parts.index("items")
        if index + 1 < len(parts):
            return parts[index + 1]
    if len(url) == 32 and all(char.isalnum() for char in url):
        return url
    return ""


def build_arcgis_map_html(df: pd.DataFrame, filters: FilterState, height: int = 620) -> str:
    station_df = latest_station_snapshot(df).copy()
    if not station_df.empty:
        station_df["fecha"] = station_df["fecha"].dt.strftime("%Y-%m-%d")
    stations = json.dumps(station_df.to_dict(orient="records"), ensure_ascii=False)
    item_id = parse_arcgis_item_id(filters.arcgis_url)
    service_url = filters.arcgis_url if filters.arcgis_url and not item_id else ""
    layers = {
        "municipios": filters.show_municipios,
        "limites": filters.show_limites,
        "estaciones": filters.show_estaciones,
    }

    # El HTML se mantiene autocontenido para integrarse en Streamlit sin servidor adicional.
    return f"""
    <html>
    <head>
      <meta charset="utf-8" />
      <meta name="viewport" content="initial-scale=1, maximum-scale=1, user-scalable=no" />
      <link rel="stylesheet" href="https://js.arcgis.com/4.30/esri/themes/light/main.css" />
      <script src="https://js.arcgis.com/4.30/"></script>
      <style>
        html, body, #viewDiv {{ padding: 0; margin: 0; height: 100%; width: 100%; }}
        #toolbar {{
          position: absolute; top: 14px; right: 14px; z-index: 2;
          background: #fff; border: 1px solid #d9e2ec; border-radius: 8px;
          padding: 10px 12px; box-shadow: 0 8px 20px rgba(31,41,55,.16);
          font-family: Arial, sans-serif; color: #1f2937; font-size: 13px;
        }}
        .legend-dot {{ display: inline-block; width: 10px; height: 10px; border-radius: 50%; background: #de3b32; margin-right: 6px; }}
      </style>
    </head>
    <body>
      <div id="viewDiv"></div>
      <div id="toolbar">
        <div><span class="legend-dot"></span>Estaciones climáticas</div>
        <div>Capas: municipios {str(layers["municipios"]).lower()}, límites {str(layers["limites"]).lower()}</div>
      </div>
      <script>
        const stations = {stations};
        const arcgisItemId = "{item_id}";
        const serviceUrl = "{service_url}";
        const showStations = {str(filters.show_estaciones).lower()};

        require([
          "esri/Map",
          "esri/WebMap",
          "esri/views/MapView",
          "esri/layers/FeatureLayer",
          "esri/layers/GraphicsLayer",
          "esri/Graphic",
          "esri/widgets/LayerList",
          "esri/widgets/Expand",
          "esri/widgets/Home",
          "esri/widgets/BasemapGallery"
        ], function(Map, WebMap, MapView, FeatureLayer, GraphicsLayer, Graphic, LayerList, Expand, Home, BasemapGallery) {{
          const map = arcgisItemId
            ? new WebMap({{ portalItem: {{ id: arcgisItemId }} }})
            : new Map({{ basemap: "topo-vector" }});

          const view = new MapView({{
            container: "viewDiv",
            map,
            center: [-75.56, 6.56],
            zoom: 8,
            popup: {{ dockEnabled: true, dockOptions: {{ position: "bottom-right", breakpoint: false }} }}
          }});

          if (serviceUrl) {{
            const climateLayer = new FeatureLayer({{
              url: serviceUrl,
              title: "Capa climática ArcGIS Online",
              outFields: ["*"],
              popupTemplate: {{
                title: "{{{{municipio}}}}",
                content: [
                  {{ type: "fields", fieldInfos: [
                    {{ fieldName: "temperatura_c", label: "Temperatura (°C)" }},
                    {{ fieldName: "precipitacion_mm", label: "Precipitación (mm)" }},
                    {{ fieldName: "altitud_m", label: "Altitud (m)" }},
                    {{ fieldName: "poblacion", label: "Población" }}
                  ] }}
                ]
              }}
            }});
            map.add(climateLayer);
          }}

          if (showStations) {{
            const stationLayer = new GraphicsLayer({{ title: "Estaciones meteorológicas" }});
            stations.forEach((station) => {{
              const graphic = new Graphic({{
                geometry: {{ type: "point", longitude: station.longitud, latitude: station.latitud }},
                symbol: {{
                  type: "simple-marker",
                  color: "#de3b32",
                  size: Math.max(8, Math.min(22, station.precipitacion_mm / 1.8)),
                  outline: {{ color: "#ffffff", width: 1.5 }}
                }},
                attributes: station,
                popupTemplate: {{
                  title: "{{municipio}} - {{estacion}}",
                  content: `
                    <b>Municipio:</b> ${{station.municipio}}<br>
                    <b>Temperatura:</b> ${{station.temperatura_c}} °C<br>
                    <b>Precipitación:</b> ${{station.precipitacion_mm}} mm<br>
                    <b>Altitud:</b> ${{station.altitud_m}} m<br>
                    <b>Coordenadas:</b> ${{station.latitud}}, ${{station.longitud}}<br>
                    <b>Población:</b> ${{Number(station.poblacion).toLocaleString("es-CO")}}
                  `
                }}
              }});
              stationLayer.add(graphic);
            }});
            map.add(stationLayer);
          }}

          view.ui.add(new Home({{ view }}), "top-left");
          view.ui.add(new Expand({{
            view,
            content: new LayerList({{ view }}),
            expandIcon: "layers",
            expanded: false
          }}), "top-left");
          view.ui.add(new Expand({{
            view,
            content: new BasemapGallery({{ view }}),
            expandIcon: "basemap",
            expanded: false
          }}), "top-left");
        }});
      </script>
    </body>
    </html>
    """
