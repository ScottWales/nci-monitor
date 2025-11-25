import sys
from pathlib import Path

sys.path.append("/opt/nci/lquota")
from lustre import LustreFilesystem


def lquota(project: str) -> list[dict]:
    result = []

    for fs in [Path("/scratch"), Path("/g/data")]:
        lfs = LustreFilesystem(str(fs))

        if (fs / project).is_dir():
            try:
                r = lfs.get_group_quota(project)
                r["fs"] = str(fs)
                if r["block_hard_limit"] > 0:
                    result.append(r)
            except Exception:
                result.append({"fs": str(fs), "group": project})
            try:
                r = lfs.get_project_quota(project)
                r["fs"] = str(fs)
                if r["block_hard_limit"] > 0:
                    result.append(r)
            except Exception:
                result.append({"fs": str(fs), "project": project})

    return result
