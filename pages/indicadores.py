import pandas as pd
import streamlit as st

from utils.helpers import (
    VARIABLES,
    apply_filters,
    configure_page,
    calculate_kpis,
    load_climate_data,
    render_header,
    render_kpi_cards,
    sidebar_filters,
)


def main() -> None:
    configure_page("Indicadores climáticos")
    df = load_climate_data()
    filters = sidebar_filters(df)
    filtered = apply_filters(df, filters)

    render_header()
    st.markdown('<div class="section-title">Indicadores climáticos</div>', unsafe_allow_html=True)
    render_kpi_cards(filtered)

    st.divider()
    st.markdown('<div class="section-title">Comparativo municipal</div>', unsafe_allow_html=True)

    aggregation = (
        filtered.groupby(["municipio", "subregion"], as_index=False)
        .agg(
            temperatura_promedio=("temperatura_c", "mean"),
            temperatura_maxima=("temperatura_c", "max"),
            temperatura_minima=("temperatura_c", "min"),
            precipitacion_acumulada=("precipitacion_mm", "sum"),
            humedad_promedio=("humedad_relativa", "mean"),
            viento_promedio=("velocidad_viento_kmh", "mean"),
            radiacion_promedio=("radiacion_solar_wm2", "mean"),
            estaciones=("estacion", "nunique"),
            poblacion=("poblacion", "max"),
        )
        .sort_values("precipitacion_acumulada", ascending=False)
    )

    st.dataframe(
        aggregation,
        use_container_width=True,
        hide_index=True,
        column_config={
            "temperatura_promedio": st.column_config.NumberColumn("Temp. promedio (°C)", format="%.1f"),
            "temperatura_maxima": st.column_config.NumberColumn("Temp. máxima (°C)", format="%.1f"),
            "temperatura_minima": st.column_config.NumberColumn("Temp. mínima (°C)", format="%.1f"),
            "precipitacion_acumulada": st.column_config.NumberColumn("Precipitación (mm)", format="%.1f"),
            "humedad_promedio": st.column_config.NumberColumn("Humedad (%)", format="%.1f"),
            "viento_promedio": st.column_config.NumberColumn("Viento (km/h)", format="%.1f"),
            "radiacion_promedio": st.column_config.NumberColumn("Radiación (W/m²)", format="%.0f"),
            "poblacion": st.column_config.NumberColumn("Población", format="%d"),
        },
    )

    csv = aggregation.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Descargar indicadores CSV",
        data=csv,
        file_name="indicadores_climaticos_antioquia.csv",
        mime="text/csv",
    )

    with st.expander("Resumen calculado"):
        kpis = calculate_kpis(filtered)
        st.json(kpis)
        st.caption(f"Variables disponibles: {', '.join(VARIABLES.keys())}")


if __name__ == "__main__":
    main()
