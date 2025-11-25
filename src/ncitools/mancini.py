from contextlib import contextmanager
from io import StringIO
import os

import pandas
import requests
from bs4 import BeautifulSoup as BS


@contextmanager
def mancini_session():
    with requests.Session() as s:
        s.headers["Origin"] = "https://my.nci.org.au"

        r = s.get("https://my.nci.org.au/mancini/login")
        r.raise_for_status()

        # Collect xsrf tokens required to log in
        soup = BS(r.text, "html.parser")
        login_form = soup.find(id="login-form")
        form = {}
        for i in login_form.find_all("input"):
            if i.get("type", None) == "submit":
                continue
            form[i["name"]] = i.get("value", None)

        # Do the login
        form["username"] = os.environ["SCHEME_USER"]
        form["password"] = os.environ["SCHEME_PASS"]
        headers = {"Referer": "https://my.nci.org.au/mancini/login"}

        r = s.post("https://my.nci.org.au/mancini/login", data=form, headers=headers)
        r.raise_for_status()

        yield s


def scheme_compute(s: requests.Session, scheme: str) -> pandas.DataFrame:
    r = s.get(f"https://my.nci.org.au/mancini/scheme/{scheme}/compute/csv", timeout=10)
    r.raise_for_status()

    return pandas.read_csv(StringIO(r.text))


def scheme_storage(s: requests.Session, scheme: str) -> pandas.DataFrame:
    r = s.get(f"https://my.nci.org.au/mancini/scheme/{scheme}/storage/csv", timeout=10)
    r.raise_for_status()

    return pandas.read_csv(StringIO(r.text))
