from collections.abc import Generator
from unittest.mock import patch

import pytest
import requests

from ncitools.mancini import scheme_compute, scheme_storage


@pytest.fixture
def session() -> Generator[requests.Session]:
    """Dummy session fixture."""
    with requests.Session() as s:
        yield s


def test_scheme_compute(session: requests.Session):
    with patch("requests.Session.get") as mock_get:
        mock_get.return_value.raise_for_status = lambda: None
        mock_get.return_value.text = "Project Code,Current Lead CI(s),Scheme,Period,Amount Allocated (kSU),Amount Used (kSU),Percentage Used (%)\nP1,CI1,Scheme1,2024.q1,100,50,50"
        df = scheme_compute(session, "bom")
        assert not df.empty
        assert all(
            col in df.columns
            for col in [
                "Project Code",
                "Current Lead CI(s)",
                "Scheme",
                "Period",
                "Amount Allocated (kSU)",
                "Amount Used (kSU)",
                "Percentage Used (%)",
            ]
        )


def test_scheme_storage(session: requests.Session):
    with patch("requests.Session.get") as mock_get:
        mock_get.return_value.raise_for_status = lambda: None
        mock_get.return_value.text = "#\n\"# 1. Amount Used is the final usage at the end of the period for past periods, and the current usage for the current period.\"\n#\nProject Code,Current Lead CI(s),Scheme,Period,Amount Allocated (KiB),Amount Used (KiB),Percentage Used (%)\nP1,CI1,Scheme1,2024.q1,100,50,50"
        df = scheme_storage(session, "bom")
        assert not df.empty
        assert all(
            col in df.columns
            for col in [
                "Project Code",
                "Current Lead CI(s)",
                "Scheme",
                "Period",
                "Amount Allocated (KiB)",
                "Amount Used (KiB)",
                "Percentage Used (%)",
            ]
        )
