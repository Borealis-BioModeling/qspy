"""
QSPy Core Model Extensions and Utilities
========================================

This module extends the PySB modeling framework with QSPy-specific features for
quantitative systems pharmacology (QSP) workflows. It provides enhanced Model and
Monomer classes, operator overloads for semantic annotation, and utilities for
metadata, logging, and summary/diagram generation.

Classes
-------
Model : QSPy extension of the PySB Model class with metadata, summary, and diagram support.
Monomer : QSPy extension of the PySB Monomer class with functional tag support.

Functions
---------
mp_lshift : Overloads '<<' for MonomerPattern/ComplexPattern to create Initial objects.
mp_invert : Overloads '~' for MonomerPattern/ComplexPattern to create Observables with auto-naming.
mp_gt : Overloads '>' for MonomerPattern/ComplexPattern to create Observables with custom names.
_make_mono_string : Utility to generate string names for MonomerPatterns.
_make_complex_string : Utility to generate string names for ComplexPatterns.

Operator Overloads
------------------
- MonomerPattern/ComplexPattern << value : Create Initial objects.
- ~MonomerPattern/ComplexPattern : Create Observable objects with auto-generated names.
- MonomerPattern/ComplexPattern > "name" : Create Observable objects with custom names.
- Monomer @ tag : Attach a functional tag to a Monomer.

Examples
--------
>>> from qspy.core import Model, Monomer
>>> m = Monomer("A", ["b"])
>>> m @ PROTEIN.LIGAND
>>> model = Model()
>>> model.with_units("nM", "min", "uL")
>>> ~m(b=None)
Observable('A_u', m(b=None))

>>> m(b=None) << 100
Initial(m(b=None), 100)
"""

from pathlib import Path
from datetime import datetime
import os
import re
from enum import Enum

import pysb.units
from pysb.units.core import *
from pysb.core import SelfExporter, MonomerPattern, ComplexPattern
import pysb.core
from qspy.config import METADATA_DIR, LOGGER_NAME, SUMMARY_DIR
from qspy.utils.logging import ensure_qspy_logging
from qspy.functionaltags import FunctionalTag
from qspy.utils.logging import log_event

__all__ = pysb.units.core.__all__.copy()


class Model(Model):
    """
    QSPy extension of the PySB Model class.

    Adds QSPy-specific utilities, metadata handling, and summary/diagram generation
    to the standard PySB Model. Supports custom units, logging, and functional tagging.

    Methods
    -------
    with_units(concentration, time, volume)
        Set simulation units for concentration, time, and volume.
    component_names
        List of component names in the model.
    qspy_metadata
        Dictionary of QSPy metadata for the model.
    summarize(path, include_diagram)
        Generate a Markdown summary of the model and optionally a diagram.
    """

    @log_event(log_args=True, static_method=True)
    @staticmethod
    def with_units(concentration: str = "mg/L", time: str = "h", volume: str = "L"):
        """
        Set simulation units for the model.

        Parameters
        ----------
        concentration : str, optional
            Concentration units (default "mg/L").
        time : str, optional
            Time units (default "h").
        volume : str, optional
            Volume units (default "L").
        """
        ensure_qspy_logging()
        SimulationUnits(concentration, time, volume)
        return

    @property
    def component_names(self):
        """
        List the names of all components in the model.

        Returns
        -------
        list of str
            Names of model components.
        """
        return [component.name for component in self.components]

    @property
    def qspy_metadata(self):
        """
        Return QSPy metadata dictionary for the model.

        Returns
        -------
        dict
            Metadata dictionary if available, else empty dict.
        """
        if hasattr(self, "qspy_metadata_tracker"):
            return self.qspy_metadata_tracker.metadata
        else:
            return {}

    @log_event(log_args=True)
    def markdown_summary(self, path=SUMMARY_DIR, include_diagram=True):
        """
        Generate a Markdown summary of the model and optionally a diagram.

        Parameters
        ----------
        path : str or Path, optional
            Output path for the summary file (default: SUMMARY_DIR).
        include_diagram : bool, optional
            Whether to include a model diagram if SBMLDiagrams is available (default: True).

        Returns
        -------
        None
        """
        lines = []
        lines.append(f"# QSPy Model Summary: `{self.name}`\n")

        metadata = self.qspy_metadata
        lines.append(f"**Model name**: `{self.name}` \n")
        lines.append(f"**Hash**: \n`{metadata.get('hash', 'N/A')}` \n")
        lines.append(f"**Version**: {metadata.get('version', 'N/A')} \n")
        lines.append(f"**Author**: {metadata.get('author', 'N/A')} \n")
        lines.append(f"**Executed by**: {metadata.get('current_user', 'N/A')} \n")
        lines.append(
            f"**Timestamp**: {metadata.get('created_at', datetime.now().isoformat())}\n"
        )

        if include_diagram and hasattr(self, "mermaid_diagram"):
            diagram_md = self.mermaid_diagram.markdown_block
            lines.append("## 🖼️ Model Diagram\n")
            lines.append(f"{diagram_md}\n")

        # Core units table
        lines.append("## Core Units\n| Quantity | Unit |")
        lines.append("|-----------|------|")
        units = getattr(self, "simulation_units", None)
        if units:
            lines.append(f"| Concentration | {units.concentration} |")
            lines.append(f"| Time         | {units.time} |")
            lines.append(f"| Volume       | {units.volume} |")
        else:
            lines.append("No core model units defined.")
            lines.append("    They can added with the `Model.with_units` method.")

        # Component counts table
        lines.append("## Numbers of Model Component\n| Component Type | Count |")
        lines.append("|---------------|-------|")
        lines += [
            f"| Monomers | {len(getattr(self, 'monomers', []))} |",
            f"| Parameters | {len(getattr(self, 'parameters', []))} |",
            f"| Expressions | {len(getattr(self, 'expressions', []))} |",
            f"| Compartments | {len(getattr(self, 'compartments', []))} |",
            f"| Rules | {len(getattr(self, 'rules', []))} |",
            f"| Initial Conditions | {len(getattr(self, 'initial_conditions', []))} |",
            f"| Observables | {len(getattr(self, 'observables', []))} |",
        ]

        # Compartments table
        lines.append("\n## Compartments\n| Name | Size |")
        lines.append("|------|------|")
        lines += [
            f"| {cpt.name} | {cpt.size.name if hasattr(cpt.size, 'name') else str(cpt.size)} |"
            for cpt in getattr(self, "compartments", [])
        ] or ["| _None_ | _N/A_ |"]

        # Monomers table
        lines.append("## Monomers\n| Name | Sites | States | Functional Tag |")
        lines.append("|------|-------|--------|---------------|")
        lines += [
            f"| {m.name} | {m.sites} | {m.site_states} | {getattr(m.functional_tag, 'value', m.functional_tag)} |"
            for m in self.monomers
        ] or ["| _None_ | _N/A_ | _N/A_ | _N/A_ |"]

        # Parameters table
        lines.append("\n## Parameters\n| Name | Value | Units |")
        lines.append("|------|--------|--------|")
        lines += [
            f"| {p.name} | {p.value} | {p.unit.to_string()} |" for p in self.parameters
        ] or ["| _None_ | _N/A_ |"]

        # Expressions table
        lines.append("\n## Expressions\n| Name | Expression |")
        lines.append("|------|------------|")
        lines += [
            f"| {e.name} | `{e.expr}` |" for e in getattr(self, "expressions", [])
        ] or ["| _None_ | _N/A_ |"]

        # Initial Conditions table
        lines.append("\n## Initial Conditions\n| Species | Value | Units |")
        lines.append("|---------|--------|--------|")
        lines += [
            f"| {str(ic[0])} | {ic[1].value if isinstance(ic[1], Parameter) else ic[1].get_value():.2f} | {ic[1].units.value}"
            for ic in self.initial_conditions
        ] or ["| _None_ | _N/A_ |"]

        def _sanitize_rule_expression(expr):
            """
            Sanitize rule expression for Markdown rendering.
            Replaces ' | ' with ' \| ' to avoid Markdown table formatting issues.
            """
            return repr(expr).replace(" | ", " \| ")
        # Rules table
        lines.append("\n## Rules\n| Name | Rule Expression | k_f | k_r | reversible |")
        lines.append("|------|-----------------|-----|-----|------------|")
        lines += [
            f"| {r.name} | `{_sanitize_rule_expression(r.rule_expression)}` | {r.rate_forward.name} | {r.rate_reverse.name if r.rate_reverse is not None else 'None'} | {r.is_reversible} |"
            for r in self.rules
        ] or ["| _None_ | _N/A_ | _N/A_ | _N/A_ | _N/A_ |"]

        # Observables table
        lines.append("\n## Observables\n| Name | Reaction Pattern |")
        lines.append("|------|------------------|")
        lines += [
            f"| {o.name} | `{o.reaction_pattern}` |" for o in self.observables
        ] or ["| _None_ | _N/A_ |"]

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
    """
    Overload the '<<' operator for MonomerPattern and ComplexPattern.

    Allows creation of Initial objects using the syntax:
        monomer_pattern << value

    Parameters
    ----------
    value : float or Parameter
        Initial value for the pattern.

    Returns
    -------
    Initial
        Initial object for the pattern.
    """
    return Initial(self, value)


pysb.core.MonomerPattern.__lshift__ = mp_lshift
pysb.core.ComplexPattern.__lshift__ = mp_lshift


translation = str.maketrans(
    {" ": "", "=": "", "(": "_", ")": "", "*": "", ",": "_", "'": ""}
)


def _make_mono_string(monopattern):
    """
    Generate a string representation for a MonomerPattern.

    Parameters
    ----------
    monopattern : MonomerPattern or str
        The monomer pattern or its string representation.

    Returns
    -------
    str
        String representation suitable for naming.
    """
    if isinstance(monopattern, MonomerPattern):
        string_repr = repr(monopattern)
    elif isinstance(monopattern, str):
        string_repr = monopattern
    else:
        raise ValueError(
            "Input pattern must a MonomerPattern or string representation of one"
        )
    # name = "place_holder"
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
            # print(bond, state)
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
            # print(bond_or_state)
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
    """
    Generate a string representation for a ComplexPattern.

    Parameters
    ----------
    complexpattern : ComplexPattern
        The complex pattern.

    Returns
    -------
    str
        String representation suitable for naming.
    """
    string_repr = repr(complexpattern)
    # Split at the bond operator '%' to
    # get the left and right-hand monomer patterns.
    mono_left, mono_right = string_repr.split("%")
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
    """
    Overload the '~' operator for MonomerPattern and ComplexPattern.

    Allows creation of Observable objects using the syntax:
        ~pattern

    Returns
    -------
    Observable
        Observable object with an auto-generated name.
    """

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
    """
    Overload the '>' operator for MonomerPattern and ComplexPattern.

    Allows creation of Observable objects with a custom name using the syntax:
        pattern > "observable_name"

    Parameters
    ----------
    other : str
        Name for the observable.

    Returns
    -------
    Observable
        Observable object with the specified name.

    Raises
    ------
    ValueError
        If the provided name is not a string.
    """
    if not isinstance(other, str):
        raise ValueError("Observable name should be a string")
    else:
        return Observable(other, self)


pysb.core.MonomerPattern.__gt__ = mp_gt
pysb.core.ComplexPattern.__gt__ = mp_gt


class Monomer(Monomer):
    """
    QSPy extension of the PySB Monomer class.

    Adds support for functional tags and operator overloading for semantic annotation.

    Methods
    -------
    __matmul__(other)
        Attach a functional tag to the monomer using the '@' operator.
    __imatmul__(other)
        Attach a functional tag to the monomer in-place using the '@=' operator.
    __repr__()
        String representation including the functional tag if present.
    """

    def __init__(self, *args, **kwargs):
        """
        Initialize a Monomer with optional functional tag.

        Parameters
        ----------
        *args, **kwargs
            Arguments passed to the PySB Monomer constructor.
        """
        self.functional_tag = FunctionalTag(
            "None", "None"
        )  # Default to no functional tag
        super().__init__(*args, **kwargs)
        return

    def __matmul__(self, other: Enum):
        """
        Attach a functional tag to the monomer using the '@' operator.

        Parameters
        ----------
        other : Enum
            Enum member representing the functional tag.

        Returns
        -------
        Monomer
            The monomer instance with the functional tag set.
        """
        if isinstance(other, Enum):
            ftag_str = other.value
            ftag = FunctionalTag(*FunctionalTag.parse(ftag_str))
            setattr(self, "functional_tag", ftag)
        return self

    def __imatmul__(self, other: Enum):
        """
        Attach a functional tag to the monomer in-place using the '@=' operator.

        Parameters
        ----------
        other : Enum
            Enum member representing the functional tag.

        Returns
        -------
        Monomer
            The monomer instance with the functional tag set.
        """
        if isinstance(other, Enum):
            ftag_str = other.value
            ftag = FunctionalTag(*FunctionalTag.parse(ftag_str))
            setattr(self, "functional_tag", ftag)
        return self

    def __repr__(self):
        """
        Return a string representation of the monomer, including the functional tag if present.

        Returns
        -------
        str
            String representation of the monomer.
        """
        if self.functional_tag is None:
            return super().__repr__()
        else:
            base_repr = super().__repr__()
            return f"{base_repr} @ {self.functional_tag.value}"
    
    def __pow__(self, compartment: Compartment):
        """
        Overload the '**' operator to allow monomers to be passed with a compartment.

        This is a shortcut for creating a MonomerPattern with a compartment:
          i.e., `monomer ** compartment` is equivalent to `monomer() ** compartment`.


        Parameters
        ----------
        compartment : Compartment
            The compartment in which the monomer pattern resides.

        Returns
        -------
        MonomerPattern
            A MonomerPattern from calling the monomer with the compartment.
        """
        if not isinstance(compartment, Compartment):
            raise TypeError("Compartment must be an instance of Compartment")
        return self() ** compartment
    
# class Compartment(Compartment):
#     """
#     QSPy extension of the PySB Compartment class.

#     This class allows for the creation of compartments with specific names and sizes.
#     It can be used to define compartments in a QSPy model.

#     Parameters
#     ----------
#     name : str
#         Name of the compartment.
#     size : float or Parameter, optional
#         Size of the compartment (default is 1.0).
#     """
    
#     def __init__(self, name: str, size: float | Parameter = 1.0):
#         super().__init__(name, size)
    
#     def __contains__(self, other: MonomerPattern | ComplexPattern | Monomer):
#         """
#         Check if a monomer pattern or complex pattern is contained within this compartment.

#         Parameters
#         ----------
#         other : MonomerPattern or ComplexPattern
#             The pattern to check for containment.

#         Returns
#         -------
#         bool
#             True if the pattern is contained in this compartment, False otherwise.
#         """
#         if not isinstance(other, (MonomerPattern, ComplexPattern)):
#             raise TypeError("Other must be a MonomerPattern, ComplexPattern, or Monomer")
#         return other ** self