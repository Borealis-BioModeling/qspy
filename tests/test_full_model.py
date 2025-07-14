import pytest

from qspy.core import (
    Model,
    Parameter,
    Monomer,
    Parameter,
    Expression,
    Rule,
    Compartment,
    Observable,
)
from qspy.contexts import (
    parameters,
    expressions,
    compartments,
    monomers,
    initials,
    rules,
    observables,
)
from qspy.functionaltags import PROTEIN
from qspy.validation import ModelMetadataTracker
from qspy.validation import ModelChecker

__version__ = "test-0.1.0"
__author__ = "test_author"

Model().with_units(concentration="mg/L", time="h", volume="L")

print("----------parameters-------------")

with parameters():
    V_1 = (10.0, "L")
    A_0 = (100.0, "mg")
    k_deg = (1e-3, "1/s")
    k_goo = (0, "1/s")

print("----------expressions-------------")

with expressions():
    C_0 = A_0 / V_1
    C_1 = 2.0 * C_0

print("----------compartments-------------")
with compartments():
    CENTRAL = V_1

print("----------monomers-------------")
with monomers():
    molec_a = (None, None)
    molec_b = (["b"], None, PROTEIN.ANTIBODY)
    molec_c = (["b", "state"], {"state": ["p", "u"]})

molec_a @= PROTEIN.PHOSPHATASE
Monomer("molec_d", ["b"]) @ PROTEIN.RECEPTOR

print("----------initials-------------")
with initials():
    molec_a() ** CENTRAL << C_0


print("----------rules-------------")
with rules():
    R_1 = (molec_a() ** CENTRAL >> None, k_deg)

print("----------observables-------------")
with observables():
    ~(molec_a() ** CENTRAL)
    ~molec_c(b=None, state="u")
    molec_c(b=None, state="p") > "C_p"

ModelMetadataTracker(__version__, author=__author__)
ModelChecker()


@pytest.mark.integration
def test_full_model():
    """
    Test the full model creation and validation process.
    This function initializes a model, sets up metadata tracking,
    and runs the model checker to validate the model.
    """
    print(model)
    assert len(model.parameters) > 0, "Model should have parameters defined"
    assert len(model.monomers) > 0, "Model should have monomers defined"
    assert len(model.rules) > 0, "Model should have rules defined"
    assert len(model.observables) > 0, "Model should have observables defined"
    assert model.qspy_metadata_tracker is not None, (
        "Model should have metadata tracker initialized"
    )
    assert model.monomers["molec_b"].functional_tag == PROTEIN.ANTIBODY, (
        "Monomer 'molec_b' should have functional tag 'ANTIBODY'"
    )
    assert hasattr(model, "simulation_units"), (
        "Model should have simulation units defined"
    )


if __name__ == "__main__":
    test_full_model()
    print("Full model test passed successfully.")
