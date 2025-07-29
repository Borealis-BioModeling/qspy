# QSPy Model Specification Example
# =========================
# This document provides an example of how to specify a model in QSPy, including the use of functional monomers, metadata tracking, and validation tools.
# This example demonstrates a simple ligand-receptor binding model with metadata tracking and validation.
# Adapted from the LR_comp.bngl model at https://github.com/RuleWorld/BNGTutorial/blob/master/CBNGL/LR_comp.bngl

from qspy import *
from pysb.units import set_molecule_volume

Model().with_units(concentration="molecules", time="s", volume="um**3")
v_cell = 1000  # Typical eukaryotic cell volume in um^3
v_ec = 1000 * v_cell  # Volume of extracellular space around each cell (1/cell density)
# Required for molecules units and conversions between molar concentrations and molecules
set_molecule_volume(v_cell, "um**3")  # Set the default molecule volume for the model

with parameters():
    Vcell = (v_cell, "um**3")  # Typical eukaryotic cell volume ~ 1000 um^3
    Vec = (
        v_ec,
        "um**3",
    )  # Volume of extracellular space around each cell (1/cell density)
    d_pm = (0.01, "um")  # Effective thickness of the plasma membrane (10 nm)
    Acell = (1000, "um**2")  # Approximate area of PM
    R0 = (10000, "molecules")  # number of receptor molecules per cell
    kp1 = (1e6, "1/(M*s)")  # Forward binding rate constant for L-R
    km1 = (0.01, "1/s")  # Reverse binding rate constant for L-R
    L0 = (1e-8, "M")  # Ligand concentration - molar

with expressions():
    Vpm = Acell * d_pm  # Effective volume of PM

# Define compartments with sizes and dimensions
# Need to use the Compartment class directly (instead of compartments context)
# to define compartments so we can set the parent compartments correctly
Compartment("EC", size=Vec, dimension=3)
Compartment(
    "PM", size=Vpm, dimension=2, parent=EC
)  # Plasma membrane is part of the extracellular space
Compartment(
    "CP", size=Vcell, dimension=3, parent=PM
)  # Cytoplasmic compartment is also part of the plasma membrane

with monomers():
    L = (["r"], None, PROTEIN.LIGAND)  # Ligand with one binding site
    R = (["l"], None, PROTEIN.RECEPTOR)  # Receptor with one binding site

with initials():
    L(r=None) ** EC << L0  # Initial ligand concentration in extracellular space
    R(l=None) ** PM << R0  # Initial receptor concentration in plasma membrane

with observables():
    R(l=None) ** PM > "FreeR"
    R(l=ANY) ** PM > "Bound"
    L(r=ANY) ** EC > "test"  # Testing if any bound ligands in EC

with rules():
    # Reversible binding reaction between ligand and receptor
    binding = (
        L(r=None) ** EC + R(l=None) ** PM | L(r=1) ** EC % R(l=1) ** PM,
        kp1,
        km1,
    )

ModelMetadataTracker(
    version="0.1.0",
    author="QSPy Example",
)
ModelMermaidDiagrammer()
# Validate the model
ModelChecker()
