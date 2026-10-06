"""
Gather all responses
"""

import argparse
import grp
import logging
import os
import pwd
from datetime import datetime, timezone
from pathlib import Path

import pandas

from ncitools.lquota import lquota
from ncitools.nci_account import nci_account, nci_account_result, process_nci_account

from .mancini import mancini_session, scheme_compute, scheme_storage

log = logging.getLogger(__name__)


def atomic_append(path: Path | str, df: pandas.DataFrame):
    """
    Append a DataFrame to a CSV file atomically.

    If the file exists, the new data is concatenated with the existing data.
    The operation is performed atomically using a temporary file.

    Args:
        path (Path|str): The path to the CSV file.
        df (pandas.DataFrame): The DataFrame to append.
    """
    path = Path(path)
    tmppath = path.with_suffix(path.suffix + ".tmp")
    if path.exists():
        df = pandas.concat([pandas.read_csv(path), df])
    df.to_csv(tmppath, index=False)
    tmppath.replace(path)


def gather_schemes(output: Path, timestamp: datetime, schemes: list[str]):

    with mancini_session() as session:
        for s in schemes:
            current_quarter = f"{timestamp.year}.q{((timestamp.month - 1) // 3) + 1}"

            log.info("Mancini %s", s)
            compute = scheme_compute(session, s)
            storage = scheme_storage(session, s)

            compute = compute[compute["Period"] == current_quarter]
            storage = storage[storage["Period"] == current_quarter]

            compute["timestamp"] = timestamp.isoformat(timespec="minutes")
            storage["timestamp"] = timestamp.isoformat(timespec="minutes")

            atomic_append(output / f"scheme-compute.csv", compute)
            atomic_append(output / f"scheme-storage.csv", storage)


def gather_projects(output: Path, schemes: list[str]) -> set[str]:
    projects: set[str] = set()
    for s in schemes:
        projects.update(
            pandas.read_csv(output / f"scheme-compute.csv")["Project Code"].unique()
        )
        projects.update(
            pandas.read_csv(output / f"scheme-storage.csv")["Project Code"].unique()
        )
    return projects


def gather_membership(output: Path, timestamp: datetime, projects: set[str]):
    records: list[dict[str, str]] = []
    for p in projects:
        g = grp.getgrnam(p)
        members = g.gr_mem

        for m in members:
            u = pwd.getpwnam(m)
            gecos = u.pw_gecos
            records.append(
                {
                    "project": p,
                    "member": m,
                    "gecos": gecos,
                    "timestamp": timestamp.isoformat(timespec="minutes"),
                }
            )

    if records:
        atomic_append(output / "membership.csv", pandas.DataFrame(records))


def getgrouplist(user: str) -> list[str]:
    gids = os.getgrouplist(user, pwd.getpwnam(user).pw_gid)
    groups = [grp.getgrgid(gid).gr_name for gid in gids]
    return groups


def gather_project_info(output: Path, timestamp: datetime, projects: list[str]):
    results: list[nci_account_result] = []
    for p in projects:
        log.info("nci_account -P %s", p)
        results.append(nci_account(p))
    r = process_nci_account(results, timestamp)
    atomic_append(output / "nci_account.compute.csv", r["compute"])
    atomic_append(output / "nci_account.storage.csv", r["storage"])


def gather_storage_info(output: Path, timestamp: datetime, projects: list[str]):
    results: list[dict[str, str | float]] = []
    for p in projects:
        log.info("lquota -P %s", p)
        results.extend(lquota(p))
    df = pandas.DataFrame(results)
    df["timestamp"] = timestamp.isoformat(timespec="minutes")
    atomic_append(output / "lquota.csv", df)


def gather(output: Path | str):
    """Gather NCI information from various sources.

    Args:
        output (Path|str): The directory where the gathered CSV files will be stored.
    """
    output = Path(output)
    timestamp = datetime.now(tz=timezone.utc)
    schemes = ["bom", "bom-acs"]

    # Gather scheme level information
    gather_schemes(output, timestamp, schemes)

    # All the projects we're interested in
    projects = gather_projects(output, schemes)

    # Gather project membership
    # gather_membership(output, timestamp, projects)

    # Gather projects we can get more info on
    my_projects = set(getgrouplist(os.getlogin()))
    gather_project_info(output, timestamp, list(projects & my_projects))
    gather_storage_info(output, timestamp, list(projects & my_projects))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Gather NCI information from various sources."
    )
    parser.add_argument(
        "output",
        type=str,
        help="The directory where the gathered CSV files will be stored.",
    )
    args = parser.parse_args()

    gather(args.output)
