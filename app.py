import streamlit as st

from utils.helpers import (
    apply_filters,
    configure_page,
    line_chart,
    load_climate_data,
    precipitation_chart,
    render_header,
    render_kpi_cards,
    sidebar_filters,
)


def main() -> None:
    configure_page()
    df = load_climate_data()
    filters = sidebar_filters(df)
    filtered = apply_filters(df, filters)

    render_header()

    st.markdown('<div class="section-title">Resumen ejecutivo</div>', unsafe_allow_html=True)
    render_kpi_cards(filtered)

    st.divider()
    left, right = st.columns((1.25, 1))
    with left:
        variable = filters.variables[0] if filters.variables else "Temperatura"
        st.markdown(f'<div class="section-title">Serie temporal de {variable.lower()}</div>', unsafe_allow_html=True)
        st.plotly_chart(line_chart(filtered, variable), use_container_width=True)
    with right:
        st.markdown('<div class="section-title">Precipitación acumulada</div>', unsafe_allow_html=True)
        st.plotly_chart(precipitation_chart(filtered), use_container_width=True)

    st.markdown(
        """
        <div class="info-panel">
          Use el menú lateral para filtrar fechas, subregiones, municipios, variables y capas.
          En la página <b>Mapa</b> puede pegar la URL de un WebMap o Feature Layer de ArcGIS Online.
        </div>
        """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
