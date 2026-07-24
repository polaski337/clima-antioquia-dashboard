import streamlit as st

from utils.helpers import (
    VARIABLES,
    apply_filters,
    configure_page,
    heatmap_chart,
    line_chart,
    load_climate_data,
    municipality_bar_chart,
    plotly_config,
    precipitation_chart,
    render_header,
    sidebar_filters,
)


def main() -> None:
    configure_page("Estadísticas climáticas")
    df = load_climate_data()
    filters = sidebar_filters(df)
    filtered = apply_filters(df, filters)

    render_header()
    st.markdown('<div class="section-title">Exploración estadística</div>', unsafe_allow_html=True)

    selected_variable = st.selectbox(
        "Variable principal",
        options=list(VARIABLES.keys()),
        index=0,
    )

    tab_temporal, tab_municipios, tab_heatmap = st.tabs(
        ["Series temporales", "Municipios", "Mapa de calor"]
    )

    with tab_temporal:
        left, right = st.columns(2)
        with left:
            st.plotly_chart(
                line_chart(filtered, selected_variable),
                use_container_width=True,
                theme=None,
                config=plotly_config(),
            )
        with right:
            st.plotly_chart(
                precipitation_chart(filtered),
                use_container_width=True,
                theme=None,
                config=plotly_config(),
            )

    with tab_municipios:
        st.plotly_chart(
            municipality_bar_chart(filtered, selected_variable),
            use_container_width=True,
            theme=None,
            config=plotly_config(),
        )

    with tab_heatmap:
        st.plotly_chart(
            heatmap_chart(filtered, selected_variable),
            use_container_width=True,
            theme=None,
            config=plotly_config(),
        )

    st.markdown('<div class="section-title">Datos filtrados</div>', unsafe_allow_html=True)
    st.dataframe(filtered.sort_values(["fecha", "municipio"]), use_container_width=True, hide_index=True)


if __name__ == "__main__":
    main()
