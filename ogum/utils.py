"""Small helper utilities used across the code base."""
from __future__ import annotations

from typing import Dict, Iterable, List

import numpy as np
import pandas as pd
try:  # pragma: no cover - optional dependency
    import ipywidgets as widgets
    from IPython.display import clear_output, display
except Exception:  # pragma: no cover - fallback stubs
    class _Dummy:
        def __getattr__(self, name):
            raise RuntimeError("ipywidgets is required for GUI functions")

    widgets = _Dummy()

    def display(*_args, **_kwargs):
        return None

    def clear_output(*_args, **_kwargs):
        return None

from .core import add_suffix_once


def normalize_columns(df: pd.DataFrame, mapping: Dict[str, Iterable[str]]) -> pd.DataFrame:
    """Return a DataFrame with columns renamed based on a mapping.

    Parameters
    ----------
    df:
        DataFrame cujos nomes de colunas serão normalizados.
    mapping:
        Dicionário onde a chave é o nome desejado e o valor é uma lista
        de nomes possíveis (case insensitive) encontrados em ``df``.
    """
    rename_dict = {}
    for col in df.columns:
        lower_col = col.lower()
        for standard, names in mapping.items():
            if any(name.lower() in lower_col for name in names):
                rename_dict[col] = standard
                break
    return df.rename(columns=rename_dict)


class EaSelectionWidget:
    """Widget para definir Energias de Ativação.

    Attributes
    ----------
    ui : widgets.VBox
        Componente raiz exibindo todos os controles.
    """

    def __init__(self) -> None:
        self._build_ui()

    def _build_ui(self) -> None:
        self.radio_energy_choice = widgets.RadioButtons(
            options=[("Discretas", "discretas"), ("Intervalo", "intervalo")],
            value="discretas",
            description="Modo de Seleção de Ea:",
            style={"description_width": "initial"},
        )
        self.dropdown_num_energies = widgets.Dropdown(
            options=[(f"{i} energias", i) for i in range(1, 11)],
            value=3,
            description="Quantidade:",
        )
        self.btn_energy_add = widgets.Button(description="Gerar Campos", button_style="info")
        self.energies_box = widgets.VBox([])

        self.float_min = widgets.FloatText(value=100.0, description="Ea Mín (kJ/mol):")
        self.float_max = widgets.FloatText(value=2000.0, description="Ea Máx (kJ/mol):")
        self.num_points = widgets.IntText(value=20, description="Nº de Pontos:")

        self.discretas_container = widgets.VBox(
            [self.dropdown_num_energies, self.btn_energy_add, self.energies_box]
        )
        self.intervalo_container = widgets.VBox(
            [self.float_min, self.float_max, self.num_points],
            layout={"display": "none"},
        )

        self.radio_energy_choice.observe(self._on_energy_choice_changed, names="value")
        self.btn_energy_add.on_click(self._on_add_energies)
        self._on_add_energies(None)

        self.ui = widgets.VBox(
            [
                widgets.HTML("<b>Definir Energias de Ativação (Ea) para Análise</b>"),
                self.radio_energy_choice,
                self.discretas_container,
                self.intervalo_container,
            ]
        )

    def _on_energy_choice_changed(self, change: Dict[str, str]) -> None:
        is_discrete = change["new"] == "discretas"
        self.discretas_container.layout.display = "" if is_discrete else "none"
        self.intervalo_container.layout.display = "none" if is_discrete else ""

    def _on_add_energies(self, _b: object) -> None:
        n = self.dropdown_num_energies.value
        self.energies_box.children = [
            widgets.FloatText(
                value=round(100.0 + 50 * i, 1), description=f"Ea {i+1} (kJ/mol):"
            )
            for i in range(n)
        ]

    def get_ea_list(self) -> List[float]:
        """Return the list of activation energies."""

        if self.radio_energy_choice.value == "discretas":
            values = [ft.value for ft in self.energies_box.children if ft.value > 0]
            if not values:
                raise ValueError("Nenhuma energia válida informada.")
            return sorted(set(values))

        ea_min = self.float_min.value
        ea_max = self.float_max.value
        n_pts = self.num_points.value
        if ea_max <= ea_min or n_pts < 2:
            raise ValueError("Ea Máx deve ser maior que Ea Mín e número de pontos >= 2.")
        return list(np.linspace(ea_min, ea_max, n_pts))


def map_mod2_dataframe(df: pd.DataFrame, rename_dict: Dict[str, str], idx: int) -> pd.DataFrame:
    """Return ``df`` after applying column mappings and conversions.

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame original carregado do arquivo.
    rename_dict : Dict[str, str]
        Mapeamento de ``coluna_original`` para ``novo_nome``.
    idx : int
        Índice (1-baseado) do ensaio utilizado para sufixar colunas.

    Returns
    -------
    pandas.DataFrame
        DataFrame processado pronto para uso.
    """

    df_temp = df[list(rename_dict.keys())].rename(columns=rename_dict).copy()

    if "Time_min" in df_temp.columns:
        df_temp["Time_s"] = df_temp.pop("Time_min") * 60.0
    elif "Time_h" in df_temp.columns:
        df_temp["Time_s"] = df_temp.pop("Time_h") * 3600.0

    if not any(c.startswith("Time") for c in df_temp.columns) or not any(
        c.startswith("Temp") for c in df_temp.columns
    ) or not any(c.startswith("Dens") or c.startswith("Retracao") for c in df_temp.columns):
        raise ValueError(
            "Mapeamento incompleto. Verifique se Tempo, Temperatura e Densidade/Retração foram mapeados."
        )

    df_temp.columns = [add_suffix_once(c, f"_e{idx}") for c in df_temp.columns]
    return df_temp


def convert_retraction_to_density(
    df: pd.DataFrame,
    idx: int,
    dens_inicial: float,
    dens_final: float,
    tamanho_inicial: float,
) -> pd.DataFrame:
    """Converte colunas de retração em densidade percentual.

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame de entrada já mapeado.
    idx : int
        Índice (1-baseado) do ensaio.
    dens_inicial : float
        Densidade inicial.
    dens_final : float
        Densidade final.
    tamanho_inicial : float
        Comprimento inicial da amostra, necessário para retracao absoluta.

    Returns
    -------
    pandas.DataFrame
        DataFrame com a coluna de densidade convertida.
    """

    target_col = f"DensidadePct_e{idx}"
    if target_col in df.columns:
        return df

    df_temp = df.copy()
    found_col = None
    retracao_rel = None
    prefixes = [("RetracaoRel", 1.0), ("RetracaoPct", 100.0), ("RetracaoAbs", tamanho_inicial)]
    for prefix, divisor in prefixes:
        col_name = f"{prefix}_e{idx}"
        if col_name in df_temp:
            if prefix == "RetracaoAbs" and tamanho_inicial <= 0:
                raise ValueError("Tamanho inicial deve ser maior que zero.")
            retracao_rel = df_temp[col_name] / divisor
            found_col = col_name
            break

    if found_col is None or retracao_rel is None:
        raise ValueError("Nenhuma coluna de retração encontrada para converter.")

    df_temp[target_col] = dens_inicial / (1 + retracao_rel) ** 3
    min_calc = df_temp[target_col].min()
    max_calc = df_temp[target_col].max()
    if max_calc > min_calc:
        df_temp[target_col] = dens_inicial + (df_temp[target_col] - min_calc) * (
            dens_final - dens_inicial
        ) / (max_calc - min_calc)

    df_temp.drop(columns=[found_col], inplace=True)
    return df_temp


def orlandini_araujo_filter(df: pd.DataFrame, bin_size: int = 10) -> pd.DataFrame:
    """Aplica o filtro de Orlandini-Araujo.

    O algoritmo agrupa os dados em janelas de ``bin_size`` segundos e
    calcula a média de tempo, temperatura e densidade de cada grupo.

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame de entrada contendo colunas ``Time_s``, ``Temperature_C`` e
        ``DensidadePct``.
    bin_size : int
        Largura da janela de agrupamento em segundos.

    Returns
    -------
    pandas.DataFrame
        DataFrame filtrado segundo o método de Orlandini-Araujo.
    """

    time_col = next((c for c in df.columns if c.startswith("Time_s")), None)
    temp_col = next((c for c in df.columns if c.startswith("Temperature_C")), None)
    dens_col = next((c for c in df.columns if c.startswith("DensidadePct")), None)

    if not (time_col and temp_col and dens_col):
        raise ValueError(
            "Faltam colunas (Time_s, Temperature_C, DensidadePct) p/ Orlandini-Araujo."
        )

    dfc = df.copy()
    dfc["bin"] = np.floor(dfc[time_col] / bin_size).astype(int)
    grouped = (
        dfc.groupby("bin").agg({time_col: "mean", temp_col: "mean", dens_col: "mean"}).reset_index(drop=True)
    )
    return grouped

__all__ = [
    "normalize_columns",
    "EaSelectionWidget",
    "map_mod2_dataframe",
    "convert_retraction_to_density",
    "orlandini_araujo_filter",
]
