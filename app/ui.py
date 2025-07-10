import pandas as pd
import requests
import streamlit as st
import plotly.graph_objects as go

API_URL = "http://localhost:8000"


def main() -> None:
    """Render Ogum interface."""
    st.title("Ogum Sintering")

    tab_simulation, tab_analysis = st.tabs(
        ["1. Simulação de Modelo", "2. Análise de Dados Experimentais"]
    )

    with tab_simulation:
        st.write("Simulação de Modelo em desenvolvimento.")

    with tab_analysis:
        file = st.file_uploader("Envie um arquivo CSV", type="csv")
        if file is not None:
            try:
                df = pd.read_csv(file)
                st.dataframe(df.head())

                x_col = st.selectbox("Eixo X (Tempo/Temperatura)", df.columns)
                y_col = st.selectbox("Eixo Y (Dados a Filtrar)", df.columns)

                window_length = st.number_input(
                    "Tamanho da janela (ímpar)", min_value=1, value=5, step=2
                )
                polyorder = st.number_input(
                    "Ordem do polinômio", min_value=1, value=2, step=1
                )

                if st.button("Aplicar Filtro e Visualizar"):
                    try:
                        payload = {
                            "data_points": df[y_col].tolist(),
                            "window_length": int(window_length),
                            "polyorder": int(polyorder),
                        }
                        response = requests.post(
                            f"{API_URL}/processing/filter", json=payload
                        )
                        response.raise_for_status()
                        filtered = response.json()["filtered_data"]

                        fig = go.Figure()
                        fig.add_trace(
                            go.Scatter(
                                x=df[x_col],
                                y=df[y_col],
                                mode="lines",
                                name="Original",
                            )
                        )
                        fig.add_trace(
                            go.Scatter(
                                x=df[x_col],
                                y=filtered,
                                mode="lines",
                                name="Filtrado",
                            )
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    except Exception as err:
                        st.error(f"Erro ao processar os dados: {err}")
            except Exception as err:
                st.error(f"Falha ao ler o arquivo: {err}")


if __name__ == "__main__":
    main()
