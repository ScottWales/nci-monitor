import getpass
import pwd
from unittest.mock import patch

from ..users import project_members


def test_project_members():
    with patch("ncitools.users.grp.getgrnam") as mock_getgrnam:
        mock_getgrnam.return_value.gr_mem = [getpass.getuser()]
        members = project_members("test")

    me = pwd.getpwnam(getpass.getuser())
    assert {"user": me.pw_name, "name": me.pw_gecos} in members
