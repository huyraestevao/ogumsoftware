import pandas as pd
import requests
import streamlit as st
import plotly.graph_objects as go
import numpy as np

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
                rate_col = st.selectbox("Taxa (ex: d(ρ)/dt)", df.columns)

                window_length = st.number_input(
                    "Tamanho da janela (ímpar)", min_value=1, value=5, step=2
                )
                polyorder = st.number_input(
                    "Ordem do polinômio", min_value=1, value=2, step=1
                )

                if st.button("Calcular Energia de Ativação (Q)"):
                    try:
                        payload = {
                            "temperatures": df[x_col].astype(float).tolist(),
                            "rates": df[rate_col].astype(float).tolist(),
                        }
                        response = requests.post(
                            f"{API_URL}/processing/activation-energy", json=payload
                        )
                        response.raise_for_status()
                        result = response.json()
                        col1, col2 = st.columns(2)
                        col1.metric(
                            "Energia de Ativação (Q)", f"{result['Q']:.2f} kJ/mol"
                        )
                        col2.metric("R²", f"{result['r_squared']:.3f}")

                        inv_T = 1.0 / df[x_col].astype(float)
                        ln_rate = np.log(df[rate_col].astype(float))
                        line = result["slope"] * inv_T + result["intercept"]
                        fig_arr = go.Figure()
                        fig_arr.add_trace(
                            go.Scatter(
                                x=inv_T,
                                y=ln_rate,
                                mode="markers",
                                name="Dados",
                            )
                        )
                        fig_arr.add_trace(
                            go.Scatter(
                                x=inv_T,
                                y=line,
                                mode="lines",
                                name="Regressão",
                            )
                        )
                        fig_arr.update_xaxes(title="1/T (1/K)")
                        fig_arr.update_yaxes(title="ln(Taxa)")
                        st.plotly_chart(fig_arr, use_container_width=True)
                    except Exception as err:
                        st.error(f"Erro ao calcular energia de ativação: {err}")

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
