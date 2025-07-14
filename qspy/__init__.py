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

from qspy.core import *

from pysb.pkpd import simulate


