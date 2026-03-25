from lib_core.data import Formalization, Requirement
from lib_pea.countertrace import Countertrace
from lib_pea.countertrace_to_pea import build_automaton
from lib_pea.pea import PhaseSetsPea


def get_pea_from_formalisation(req: Requirement, f: Formalization, i: int, ct: Countertrace) -> PhaseSetsPea:
    sfid = f"c_{req.rid}_{f.id}_{i}_"
    return build_automaton(ct, sfid)
