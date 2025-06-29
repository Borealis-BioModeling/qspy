from pathlib import Path
from datetime import datetime
import os
import re
from enum import Enum
from pysb.export import export as pysb_export

try:
    import SBMLDiagrams

    HAS_SBMLDIAGRAMS = True
except ImportError:
    HAS_SBMLDIAGRAMS = False
import pysb.units
from pysb.units.core import *
from pysb.core import SelfExporter, MonomerPattern, ComplexPattern
import pysb.core
from metadata import METADATA_DIR
from utils.logging import ensure_qspy_logging
from functionaltags import FunctionalTag
from utils.logging import log_event, LOGGER_NAME

__all__ = pysb.units.core.__all__

SUMMARY_DIR = METADATA_DIR + "/model_summary.md"


class Model(Model):
    # def __init__(
    #     self,
    #     name=None,
    #     base=None,
    #     units={"concentration": "mg/L", "time": "h", "volume": "L"},
    # ):
    #     super().__init__(name='model', base=base)
    #     #SelfExporter.export(self)
    #     SimulationUnits(**units)
    #     return
    @log_event(log_args=True, static_method=True)
    @staticmethod
    def with_units(concentration: str = "mg/L", time: str = "h", volume: str = "L"):
        ensure_qspy_logging()
        SimulationUnits(concentration, time, volume)
        return

    @property
    def component_names(self):
        return [component.name for component in self.components]

    @property
    def qspy_metadata(self):
        if hasattr(self, "qspy_metadata_tracker"):
            return self.qspy_metadata_tracker.metadata
        else:
            return {}

    @log_event(log_args=True)
    def summarize(self, path=SUMMARY_DIR, include_diagram=True):
        """Generate a Markdown summary of the model and optionally a diagram."""
        lines = []
        lines.append(f"# QSPy Model Summary: `{self.name}`\n")

        metadata = self.qspy_metadata
        lines.append(f"**Model name**: `{self.name}`")
        lines.append(f"**Hash**: `{metadata.get('hash', 'N/A')}`")
        lines.append(f"**Version**: {metadata.get('version', 'N/A')}")
        lines.append(f"**Author**: {metadata.get('author', 'N/A')}")
        lines.append(f"**Executed by**: {metadata.get('current_user', 'N/A')}")
        lines.append(
            f"**Timestamp**: {metadata.get('created_at', datetime.now().isoformat())}\n"
        )

        if include_diagram and HAS_SBMLDIAGRAMS:
            diagram_path = Path(".qspy/model_diagram.png")
            diagram_path.parent.mkdir(parents=True, exist_ok=True)
            sbml_str = pysb_export(self, "sbml")
            with open(".qspy/temp_model.xml", "w") as f:
                f.write(sbml_str)
            diagram = SBMLDiagrams.load(".qspy/temp_model.xml")
            diagram.draw(output_file=str(diagram_path))
            lines.append("## 🖼️ Model Diagram\n")
            lines.append(f"![Model Diagram]({diagram_path})\n")

        lines.append("## Monomers")
        lines += [
            f"- `{m.name}` with sites `{m.sites}` and states `{m.site_states}` and CLASS::FUNCTION `{m.functional_tag}`"
            for m in self.monomers
        ] or ["_None defined_"]

        lines.append("\n## Parameters\n| Name | Value | Units |")
        lines.append("|------|--------|--------|")
        lines += [
            f"| {p.name} | {p.value} | {p.unit.to_string()} |" for p in self.parameters
        ] or ["| _None_ | _N/A_ |"]

        lines.append("\n## Initial Conditions\n| Species | Value | Units |")
        lines.append("|---------|--------|--------|")
        lines += [
            f"| {str(ic[0])} | {ic[1].value if isinstance(ic[1], Parameter) else ic[1].get_value()} | {ic[1].units.value}"
            for ic in self.initial_conditions
        ] or ["| _None_ | _N/A_ |"]

        lines.append("\n## Rules")
        lines += [f"- `{repr(r)}`" for r in self.rules] or ["_None defined_"]

        lines.append("\n## Observables")
        lines += [f"- `{o.name}`" for o in self.observables] or ["_None defined_"]

        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))


# patch the MonomerPattern object
# so we use a special operator with pattern:
#     monomer_patter operator value
# Applying the operator will
# create the corresponding Initial object.


def mp_lshift(self, value):
    return Initial(self, value)


pysb.core.MonomerPattern.__lshift__ = mp_lshift
pysb.core.ComplexPattern.__lshift__ = mp_lshift


translation = str.maketrans(
    {" ": "", "=": "", "(": "_", ")": "", "*": "", ",": "_", "'": ""}
)


def _make_mono_string(monopattern):
    if isinstance(monopattern, MonomerPattern):
        string_repr = repr(monopattern)
    elif isinstance(monopattern, str):
        string_repr = monopattern
    else:
        raise ValueError('Input pattern must a MonomerPattern or string representation of one')
    #name = "place_holder"
    # Get the text (if any) inside the parenthesis [e.g., molecule(b=None)]
    parenthetical = re.search("\((.*)\)", string_repr).group(0).strip("(").strip(")")
    mono = string_repr.split("(")[0]
    comp = ""
    # Get the compartment string if included in the pattern
    if "**" in string_repr:
        comp = string_repr.split("**")[1].replace(" ", "")
    if parenthetical:
        # Check for bond and state info [(b=None, state='p')]
        # NOTE - does not account for multiple bonding sites
        if "," in parenthetical:
            bond, state = parenthetical.split(",")
            bond = bond.split("=")[1]
            state = state.split("'")[1]
            print(bond, state)
            if bond == "None":
                if comp:
                    # None bond w/ state and compartment
                    name = f"{mono}_{state}_{comp}"

                else:
                    # None bond with state - no compartment
                    name = f"{mono}_{state}"
            else:
                # Include bond, state, and compartment
                name = f"{mono}_{bond}_{state}_{comp}"

        else:
            # Get bond or state info when only one is present (not both) [e.g., (b=None) or (state='u')]
            bond_or_state = parenthetical.split("=")[1].replace("'", "")
            print(bond_or_state)
            if comp:
                # Bond/state and compartment
                name = f"{mono}_{bond_or_state}_{comp}"
            else:
                # Bond/state - no compartment
                name = f"{mono}_{bond_or_state}"
    else:
        # No bond or state info [e.g., empty parenthesis ()]
        if comp:
            # With compartment
            name = f"{mono}_{comp}"
        else:
            # No compartment
            name = f"{mono}"
    return name

def _make_complex_string(complexpattern):
    string_repr = repr(complexpattern)
    # Split at the bond operator '%' to 
    # get the left and right-hand monomer patterns.
    mono_left, mono_right = string_repr.split('%')
    # Process each monomer pattern:
    name_left = _make_mono_string(mono_left)
    name_right = _make_mono_string(mono_right)
    name = f"{name_left}_{name_right}"
    return name

# Make observable definition availabe with 
# the iversion '~' prefix operator and an 
# auto generated name based on the monomer or complex
# pattern string:
#    ~pattern , e.g.:
#    ~molecA() # name='molecA'
def mp_invert(self):

    if isinstance(self, MonomerPattern):
        name = _make_mono_string(self)

    elif isinstance(self, ComplexPattern):
        name = _make_complex_string(self)

    # name = 'gooo'
    return Observable(name, self)


pysb.core.MonomerPattern.__invert__ = mp_invert
pysb.core.ComplexPattern.__invert__ = mp_invert

# Make observable definition availabe with 
# the greater than sign '>' operator:
#    pattern > "observable_name", e.g.:
#    molecA() > "A"
def mp_gt(self, other):
    if not isinstance(other, str):
        raise ValueError("Observable name should be a string")
    else:
        return Observable(other, self)

pysb.core.MonomerPattern.__gt__ = mp_gt
pysb.core.ComplexPattern.__gt__ = mp_gt

class Monomer(Monomer):

    def __init__(self, *args, **kwargs):
        self.functional_tag = None
        super().__init__(*args, **kwargs)
        return

    def __matmul__(self, other: Enum):
        if isinstance(other, Enum):
            ftag_str = other.value
            ftag = FunctionalTag(*FunctionalTag.parse(ftag_str))
            setattr(self, "functional_tag", ftag)
        return self

    def __imatmul__(self, other: Enum):
        if isinstance(other, Enum):
            ftag_str = other.value
            ftag = FunctionalTag(*FunctionalTag.parse(ftag_str))
            setattr(self, "functional_tag", ftag)
        return self

    def __repr__(self):
        if self.functional_tag is None:
            return super().__repr__()
        else:
            base_repr = super().__repr__()
            return f"{base_repr} @ {self.functional_tag.value}"
