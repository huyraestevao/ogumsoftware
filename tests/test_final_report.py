import pandas as pd

from ogum import SinteringDataRecord, FinalReportModule


def _make_record():
    df = pd.DataFrame({
        "Time_s": [0, 1, 2, 3, 4],
        "Temperature_C": [300, 320, 340, 360, 380],
        "DensidadePct": [10, 20, 40, 60, 80],
    })
    return SinteringDataRecord(ensaio_id=0, Ea=50.0, tipo_dado_y="densidade_original", df=df)


def test_final_report_instantiates():
    mod = FinalReportModule([_make_record()])
    assert isinstance(mod, FinalReportModule)


def test_generate_report_runs():
    mod = FinalReportModule([_make_record()])
    mod._on_generate_report(None)
