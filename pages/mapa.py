import streamlit as st
import streamlit.components.v1 as components

from utils.helpers import (
    apply_filters,
    build_arcgis_map_html,
    configure_page,
    latest_station_snapshot,
    load_climate_data,
    render_header,
    sidebar_filters,
)


def main() -> None:
    configure_page("Mapa climático de Antioquia")
    df = load_climate_data()
    filters = sidebar_filters(df)
    filtered = apply_filters(df, filters)

    render_header()
    st.markdown('<div class="section-title">Mapa interactivo ArcGIS</div>', unsafe_allow_html=True)

    components.html(build_arcgis_map_html(filtered, filters), height=640, scrolling=False)

    st.markdown('<div class="section-title">Detalle por municipio y estación</div>', unsafe_allow_html=True)
    snapshot = latest_station_snapshot(filtered)
    st.dataframe(
        snapshot[
            [
                "municipio",
                "subregion",
                "estacion",
                "temperatura_c",
                "precipitacion_mm",
                "altitud_m",
                "latitud",
                "longitud",
                "poblacion",
            ]
        ],
        use_container_width=True,
        hide_index=True,
        column_config={
            "temperatura_c": st.column_config.NumberColumn("Temperatura (°C)", format="%.1f"),
            "precipitacion_mm": st.column_config.NumberColumn("Precipitación (mm)", format="%.1f"),
            "altitud_m": st.column_config.NumberColumn("Altitud (m)", format="%.0f"),
            "poblacion": st.column_config.NumberColumn("Población", format="%d"),
        },
    )


if __name__ == "__main__":
    main()
