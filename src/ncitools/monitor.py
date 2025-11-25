import pandas
from .mancini import mancini_session, scheme_compute, scheme_storage


def monitor_scheme():
    records: dict[str, pandas.DataFrame] = {}
    scheme = "bom"

    with mancini_session() as s:
        records["scheme_compute"] = scheme_compute(s, scheme)
        records["scheme_storage"] = scheme_storage(s, scheme)

    projects = set(records["scheme_compute"]["project"].unique())
    projects += set(records["scheme_storage"]["project"].unique())

    print(projects)

monitor_scheme()
