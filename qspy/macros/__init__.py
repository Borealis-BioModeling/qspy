from pysb import macros as core  # Import core PySB macros
from pysb.pkpd import macros as pkpd  # Import PySB PK/PD macros
from pysb.units import add_macro_units

# Add units to both core and PK/PD macros
add_macro_units(core)
add_macro_units(pkpd)

__all__ = ["core", "pkpd"]
