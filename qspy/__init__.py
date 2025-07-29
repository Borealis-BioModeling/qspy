"""
QSPy: Quantitative Systems Pharmacology Modeling Toolkit
=======================================================

QSPy is an open-source Python package for building, simulating, and analyzing
quantitative systems pharmacology (QSP) models. It provides a modern, extensible
API for model construction, metadata tracking, reproducibility, and integration
with the PySB and scientific Python ecosystem.

Modules
-------
- Model construction and context managers
- Metadata tracking and export
- Model summary generation
- Logging utilities
- Integration with PySB PKPD simulation tools

"""

from qspy.config import QSPY_VERSION

__version__ = QSPY_VERSION

from qspy.core import *  # Import core model components
from qspy.contexts import *  # Import context managers for parameters, expressions, compartments, etc.
from qspy.validation import (
    ModelMetadataTracker,
    ModelChecker,
)  # Import validation tools
from qspy.utils.diagrams import (
    ModelMermaidDiagrammer,
)  # Import diagram generation tools
from qspy.functionaltags import *  # Import functional tags for model components
from pysb.pkpd import simulate


__all__ = [
    "Model",
    "Parameter",
    "Monomer",
    "Expression",
    "Rule",
    "Compartment",
    "Observable",
    "Initial",
    "ANY",
    "WILD",
    "parameters",
    "expressions",
    "compartments",
    "monomers",
    "initials",
    "rules",
    "observables",
    "macros",
    "simulate",
    "ModelMetadataTracker",
    "ModelChecker",
    "ModelMermaidDiagrammer",
    "PROTEIN",
    "DRUG",
    "RNA",
    "DNA",
    "METABOLITE",
    "ION",
    "LIPID",
    "NANOPARTICLE",
]
