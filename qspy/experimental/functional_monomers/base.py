"""
FunctionalMonomer base classes and mixins for QSPy experimental functional monomer API.

Provides:
- FunctionalMonomer: base class for monomers with functional tags and base states.
- BindMixin: mixin for binding macro methods.
- SynthesizeMixin: mixin for synthesis macro methods.
- DegradeMixin: mixin for degradation macro methods.
"""

from abc import ABC, abstractmethod
from ..core import Monomer, Parameter, Compartment, MonomerPattern
from pysb.macros import bind, synthesize, catalyze, degrade, catalyze_state
from pysb.core import ComponentSet
from pysb.pkpd.macros import _check_for_monomer


class FunctionalMonomer(Monomer):
    """
    Base class for functional monomers in QSPy.

    Adds support for binding sites, site states, functional tags, and a base state.
    """

    _sites = None
    _site_states = None
    _functional_tag = None
    _base_state = dict()

    def __init__(self, name: str):
        """
        Initialize a FunctionalMonomer.

        Parameters
        ----------
        name : str
            Name of the monomer.
        """
        super(FunctionalMonomer, self).__init__(name, self._sites, self._site_states)
        self @= self._functional_tag
        return

    @property
    def binding_sites(self) -> list:
        """
        List of binding sites for this monomer.

        Returns
        -------
        list
            List of binding site names.
        """
        return self._sites

    @property
    def states(self) -> dict:
        """
        Dictionary of site states for this monomer.

        Returns
        -------
        dict
            Dictionary mapping site names to possible states.
        """
        return self._site_states

    @property
    def base_state(self) -> dict:
        """
        Dictionary of base state values for this monomer.

        Returns
        -------
        dict
            Dictionary of base state assignments.
        """
        return self._base_state


class BindMixin:
    """
    Mixin class providing a binds() method for binding reactions.
    """

    def binds(
        self,
        site: str,
        other: Monomer | MonomerPattern | FunctionalMonomer,
        other_site: str,
        k_f: float | Parameter,
        k_r: float | Parameter,
        compartment: None | Compartment = None,
    ) -> ComponentSet:
        """
        Create a reversible binding reaction between this monomer and another.

        Parameters
        ----------
        site : str
            Binding site on this monomer.
        other : Monomer, MonomerPattern, or FunctionalMonomer
            The other monomer or pattern to bind.
        other_site : str
            Binding site on the other monomer.
        k_f : float or Parameter
            Forward rate constant.
        k_r : float or Parameter
            Reverse rate constant.
        compartment : Compartment or None, optional
            Compartment for the reaction (default: None).

        Returns
        -------
        ComponentSet
            PySB ComponentSet for the binding reaction.
        """
        if compartment is None:
            return bind(self, site, other, other_site, klist=[k_f, k_r])
        else:
            return bind(
                _check_for_monomer(self, compartment),
                site,
                _check_for_monomer(other, compartment),
                other_site,
                klist=[k_f, k_r],
            )


class SynthesizeMixin:
    """
    Mixin class providing a synthesized() method for synthesis reactions.
    """

    def synthesized(
        self, k_syn: float | Parameter, compartment: None | Compartment = None
    ) -> ComponentSet:
        """
        Create a synthesis reaction for this monomer.

        Parameters
        ----------
        k_syn : float or Parameter
            Synthesis rate constant.
        compartment : Compartment or None, optional
            Compartment for the reaction (default: None).

        Returns
        -------
        ComponentSet
            PySB ComponentSet for the synthesis reaction.
        """
        if compartment is None:
            return synthesize(
                self(**self.base_state),
                k_syn,
            )
        else:
            return synthesize(
                _check_for_monomer(self(**self.base_state), compartment),
                k_syn,
            )


class DegradeMixin:
    """
    Mixin class providing a degraded() method for degradation reactions.
    """

    def degraded(
        self,
        state: dict,
        k_deg: float | Parameter,
        compartment: None | Compartment = None,
    ):
        """
        Create a degradation reaction for this monomer in a given state.

        Parameters
        ----------
        state : dict
            State assignment for the monomer.
        k_deg : float or Parameter
            Degradation rate constant.
        compartment : Compartment or None, optional
            Compartment for the reaction (default: None).

        Returns
        -------
        ComponentSet
            PySB ComponentSet for the degradation reaction.
        """
        if compartment is None:
            return degrade(
                self(**state),
                k_deg,
            )
        else:
            return degrade(
                _check_for_monomer(self(**state), compartment),
                k_deg,
            )

