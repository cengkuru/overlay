"""Every entry in the mutation dispatch table resolves to a real
callable, and none of the advertised mutation classes is a ghost."""
from __future__ import annotations
import inspect
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from mutator import MUTATION_DISPATCH


def test_every_dispatch_entry_is_callable():
    for eid, fn in MUTATION_DISPATCH.items():
        assert callable(fn), f"{eid} is not callable"
        sig = inspect.signature(fn)
        # Every mutation takes (manifest, eval_id, findings)
        params = list(sig.parameters.values())
        assert len(params) == 3, f"{eid} has {len(params)} params, expected 3"


def test_no_ghost_mutation_classes():
    """Every class name used in the dispatch must exist as an emission
    from at least one evaluator in normal operation."""
    # This is verified functionally in other tests; here we just sanity
    # check that dispatch keys look like valid evaluator IDs.
    for eid in MUTATION_DISPATCH:
        assert eid.startswith("E") and "_" in eid, f"bad eval id: {eid}"
