# Ogum Sintering – versão clean 🚀
[![CI](https://github.com/huyraestevao/ogumsoftware/actions/workflows/ci.yml/badge.svg)](https://github.com/huyraestevao/ogumsoftware/actions/workflows/ci.yml)

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
de utilidades comuns localizadas em `ogum/utils.py`. Manter esse arquivo
presente permite que os scripts exportados funcionem sem ajustes adicionais.
