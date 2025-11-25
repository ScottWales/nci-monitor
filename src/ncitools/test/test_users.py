import os
import grp
import pwd
import getpass

from ..users import project_members


def test_project_members():
    members = project_members(grp.getgrgid(os.getgid()).gr_name)

    me = pwd.getpwnam(getpass.getuser())
    assert {"user": me.pw_name, "name": me.pw_gecos} in members
