# Ogum Sintering – versão clean 🚀
[![CI](https://github.com/huyraestevao/ogumsoftware/actions/workflows/ci.yml/badge.svg)](https://github.com/huyraestevao/ogumsoftware/actions/workflows/ci.yml) [![pytest](https://github.com/huyraestevao/ogumsoftware/actions/workflows/pytest.yml/badge.svg)](https://github.com/huyraestevao/ogumsoftware/actions/workflows/pytest.yml)

Este repositório contém quatro experimentos (64, 72, 80 e FZEA) em formato
Jupyter (`notebooks/`) e seus correspondentes módulos Python (`ogum/`).

## Instalação rápida
```bash
pip install -r requirements.txt
pytest -q
```

## Estrutura do código
O diretório `ogum/` reúne os módulos Python gerados a partir dos notebooks em
`notebooks/`. Esses notebooks são exportados para arquivos `.py` que dependem
de utilidades comuns localizadas em `ogum/utils.py`. Esse módulo concentra
funções auxiliares simples, como `normalize_columns`, utilizadas por diferentes
experimentos. Manter esse arquivo presente permite que os scripts exportados
funcionem sem ajustes adicionais e compartilhem a mesma base de utilidades.

O módulo `ogum/sovs.py` fornece `SOVSSolver`, um integrador baseado no modelo
de Skorohod-Olevsky. Instancie-o com os parâmetros do material e utilize
``solve(t, T)`` para obter a evolução da densidade relativa ao longo do tempo.

## Solver SOVS

O solver integra a equação

``dx/dt = A * exp(-Ea/(R T)) * (1 - x) * x**n``

onde ``R`` é a constante dos gases ideais. Um uso típico é:

```python
import numpy as np
import matplotlib.pyplot as plt
from ogum.sovs import SOVSSolver

solver = SOVSSolver(Ea=3.1e5, A=1e6, n=1.5)
t = np.linspace(0, 3600, 50)
T = np.full_like(t, 1373)
x = solver.solve(t, T)

plt.plot(t, x)
plt.xlabel("t (s)")
plt.ylabel("x")
plt.show()
```

## Estilo & Lint
O projeto utiliza o [Ruff](https://docs.astral.sh/ruff/) tanto para lint quanto
para formatação de código, substituindo o Black tradicional. Para checar se o
código segue as regras configuradas, execute:

```bash
ruff check .
```

Já a formatação pode ser aplicada com o Black embutido no Ruff:

```bash
ruff format .
```
