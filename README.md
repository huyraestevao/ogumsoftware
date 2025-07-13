# Ogum Sintering – versão clean 🚀
[![CI](https://github.com/huyraestevao/ogumsoftware/actions/workflows/ci.yml/badge.svg)](https://github.com/huyraestevao/ogumsoftware/actions/workflows/ci.yml) [![pytest](https://github.com/huyraestevao/ogumsoftware/actions/workflows/pytest.yml/badge.svg)](https://github.com/huyraestevao/ogumsoftware/actions/workflows/pytest.yml)
[![codecov](https://img.shields.io/codecov/c/github/huyraestevao/ogumsoftware/main.svg)](https://codecov.io/gh/huyraestevao/ogumsoftware)


Este repositório contém quatro experimentos (64, 72, 80 e FZEA) em formato
Jupyter (`notebooks/`) e seus correspondentes módulos Python (`src/ogum/`).

## 🚀 Acesso Online
Após cada `push` para o branch `main`, a aplicação é automaticamente publicada no Google Cloud Run. Para aceder:

1.  Vá para a secção **"Actions"** do repositório no GitHub.
2.  Encontre o último workflow de **"Deploy"** que foi executado com sucesso.
3.  Dentro dos logs do job `deploy-to-cloud-run`, irá encontrar a URL do serviço, que se parecerá com: `https://ogumsoftware-xxxxxxxx-uc.a.run.app`.

Pode também gerir os seus serviços diretamente no [Google Cloud Run Console](https://console.cloud.google.com/run).

## Instalação rápida
```bash
pip install -r requirements.txt
pip install -e .
pytest -q
```

Alguns testes de FEM e da API exigem dependências extras:

```bash
pip install fenics-dolfinx fastapi httpx
```

## 🚢 Deploy com Docker & Voila

```bash
docker-compose up --build
```
O comando agora executa a aplicação interativa completa.
Você acessa a interface Voila em [http://localhost:8866](http://localhost:8866)
e a API em [http://localhost:8000](http://localhost:8000) com docs em
[http://localhost:8000/docs](http://localhost:8000/docs)

## Estrutura do código
O diretório `src/ogum/` reúne os módulos Python gerados a partir dos notebooks em
`notebooks/`. Esses notebooks são exportados para arquivos `.py` que dependem
de utilidades comuns localizadas em `src/ogum/utils.py`. Esse módulo concentra
funções auxiliares simples, como `normalize_columns`, utilizadas por diferentes
experimentos. Manter esse arquivo presente permite que os scripts exportados
funcionem sem ajustes adicionais e compartilhem a mesma base de utilidades.

O módulo `src/ogum/sovs.py` fornece `SOVSSolver`, um integrador baseado no modelo
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

## Stub FEM
O arquivo `src/ogum/fem_interface.py` define a função `create_unit_mesh`, que apenas importa o construtor de malha do FEniCSx. Essa implementação é provisória e servirá de base para integrações futuras com um solver de Elementos Finitos.
