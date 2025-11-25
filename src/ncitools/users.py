import grp
import pwd


def project_members(project: str) -> list[dict[str, str]]:
    """
    Returns members of a project
    """
    results = []

    g = grp.getgrnam(project)
    for u in [pwd.getpwnam(m) for m in g.gr_mem]:
        results.append({"user": u.pw_name, "name": u.pw_gecos})

    return results
