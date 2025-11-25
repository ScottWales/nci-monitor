import grp
import os
from datetime import datetime
import pandas

from .nci_account import nci_account, process_nci_account


def all_projects() -> list[str]:
    return [grp.getgrgid(g).gr_name for g in {os.getgid(), *os.getgroups()}]


def collate_all(projects: list[str]) -> dict[str, pandas.DataFrame]:
    results: dict[str, pandas.DataFrame] = {}
    results |= collate_nci_account(projects)

    return results


def collate_nci_account(
    projects: list[str] | None = None, timestamp: datetime | None = None
) -> dict[str, pandas.DataFrame]:
    if timestamp is None:
        timestamp = datetime.now()
    if projects is None:
        projects = all_projects()

    records = process_nci_account([nci_account(p) for p in projects])

    return records
