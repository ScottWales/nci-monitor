"""
Gather all responses
"""

from .mancini import mancini_session, scheme_compute, scheme_storage


def gather():

    schemes = ["bom", "bom-acs"]

    with mancini_session() as session:
        for s in schemes:
            compute = scheme_compute(session, s)
            storage = scheme_storage(session, s)

    pass