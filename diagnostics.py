#!/usr/bin/env python
"""Diagnóstico rápido do ambiente Ogum Sintering.

Execute localmente com::

    python diagnostics.py
"""

from __future__ import annotations

import importlib
import os
import subprocess
import sys
from pathlib import Path

# -----------------------------------------------------------------------------#
#  CONFIGURAÇÕES MÍNIMAS
# -----------------------------------------------------------------------------#
REQUIRED_PY = (3, 11)
REQUIRED_PKGS = {
    "numpy": "1.26",
    "pandas": "2.2",
    "scipy": "1.13",
    "pytest": "8.4",
}
# -----------------------------------------------------------------------------#


def header(title: str) -> None:
    print(f"\n{'=' * 10} {title} {'=' * 10}")


# -----------------------------------------------------------------------------#
# 1. Verificações de versão
# -----------------------------------------------------------------------------#
def check_versions() -> bool:
    header("VERSÕES")
    ok = True

    # --- Python ---------------------------------------------------------------
    py_status = (
        "OK"
        if sys.version_info >= REQUIRED_PY
        else f"FAIL (≥{REQUIRED_PY[0]}.{REQUIRED_PY[1]})"
    )
    print(f"Python {sys.version.split()[0]}  {py_status}")
    ok &= py_status == "OK"

    # --- Pacotes --------------------------------------------------------------
    for pkg, wanted in REQUIRED_PKGS.items():
        try:
            mod = importlib.import_module(pkg)
            have = mod.__version__
            status = "OK" if have >= wanted else f"FAIL (≥{wanted})"
        except ModuleNotFoundError:
            have = "—"
            status = "NOT INSTALLED"
            ok = False
        print(f"{pkg:<8} {have:<10} {status}")
    return ok


# -----------------------------------------------------------------------------#
# 2. Smoke‑test de importação dos sub‑módulos principais
# -----------------------------------------------------------------------------#
def smoke_import() -> bool:
    header("IMPORT SMOKE‑TEST (ogum.*)")
    ok = True
    root = Path(__file__).resolve().parent
    sys.path.insert(0, str(root))
    for sub in ["ogum.core", "ogum.material_calibrator", "ogum.processing"]:
        try:
            importlib.import_module(sub)
            print(f"✓ {sub}")
        except Exception as exc:  # noqa: BLE001  (queremos capturar qualquer erro)
            ok = False
            print(f"✗ {sub}  —  {exc.__class__.__name__}: {exc}")
    return ok


# -----------------------------------------------------------------------------#
# 3. Execução da suíte pytest do repositório
# -----------------------------------------------------------------------------#
def run_pytest() -> bool:
    header("PYTEST SUITE")
    try:
        subprocess.run(
            ["pytest", "-q"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        print("✓ All unit tests passed")
        return True
    except subprocess.CalledProcessError as exc:
        print("✗ pytest failures:\n")
        print(exc.stdout.decode())
        return False


# -----------------------------------------------------------------------------#
# 4. Teste funcional rápido (calibração sintética)
# -----------------------------------------------------------------------------#
def functional() -> bool:
    header("TESTE FUNCIONAL RÁPIDO")
    import numpy as np
    from ogum.material_calibrator import MaterialCalibrator

    ea_true, a_true = 60.0, 2.0
    t = np.linspace(0, 5, 50)
    df = MaterialCalibrator.simulate_synthetic(ea_true, a_true, t)
    ea_fit, _ = MaterialCalibrator.fit(df)

    print(f"Ea_fit = {ea_fit:.2f} kJ/mol  (esperado ≈60 ±30%)")
    if np.isclose(ea_fit, ea_true, rtol=0.30):
        print("✓ Dentro da tolerância")
        return True
    print("✗ Fora da tolerância")
    return False


# -----------------------------------------------------------------------------#
# 5. Orquestrador interno (_run)
# -----------------------------------------------------------------------------#
def _run(*, include_tests: bool = True) -> bool:
    """Executa todas as verificações.

    Se *include_tests* for ``False`` (caso do comando ``ogum doctors``),
    **não** executa o pytest interno para evitar recursão.
    """
    checks = [
        check_versions(),
        smoke_import(),
        functional(),
    ]
    if include_tests:
        checks.insert(2, run_pytest())  # mantém a mesma ordem original

    ok = all(checks)
    header("RESULTADO FINAL")
    print("✅ Ambiente estável" if ok else "❌ Problemas detectados")
    return ok


# -----------------------------------------------------------------------------#
# 6. API pública (usada pela CLI e pelos testes)
# -----------------------------------------------------------------------------#
def run_diagnostics() -> bool:
    """Executa o diagnóstico **sem** chamar pytest interno."""
    return _run(include_tests=False)


# -----------------------------------------------------------------------------#
# 7. Entry‑point para linha de comando
# -----------------------------------------------------------------------------#
def main() -> None:
    """Roda diagnóstico completo (incluindo pytest) e encerra com exit‑code."""
    ok = _run(include_tests=True)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
