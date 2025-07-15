lint:
	ruff check src

format:
	ruff format src

test:
	pytest -q

docs:
	sphinx-build -b html docs docs/_build/html

diag:
	python scripts/build_diagnostics.py
