"""
Functional monomer protein classes and mixins for QSPy experimental API.

Provides:
- TurnoverMixin: mixin for synthesis and degradation reactions.
- Ligand: class for ligand monomers with binding functionality.
- Receptor: class for receptor monomers with orthosteric/allosteric binding and activation.
"""

from ..core import Parameter, Compartment
from ..functionaltags import *
from .base import FunctionalMonomer, BindMixin, SynthesizeMixin, DegradeMixin
from .macros import activate_concerted
from pysb.core import ComponentSet


class TurnoverMixin(DegradeMixin, SynthesizeMixin):
    """
    Mixin class providing a turnover() method for synthesis and degradation reactions.
    """

    def turnover(
        self,
        k_syn: float | Parameter,
        k_deg: float | Parameter,
        compartment: None | Compartment = None,
    ) -> ComponentSet:
        """
        Create synthesis and degradation reactions for this monomer.

        Parameters
        ----------
        k_syn : float or Parameter
            Synthesis rate constant.
        k_deg : float or Parameter
            Degradation rate constant.
        compartment : Compartment or None, optional
            Compartment for the reactions (default: None).

        Returns
        -------
        ComponentSet
            Combined PySB ComponentSet for synthesis and degradation.
        """
        components_syn = self.synthesized(k_syn, compartment=compartment)
        components_deg = self.degraded({}, k_deg, compartment=compartment)
        return components_syn | components_deg


class Ligand(BindMixin, FunctionalMonomer):
    """
    Class representing a ligand monomer with binding functionality.
    """

    _sites = ["b"]
    _functional_tag = PROTEIN.LIGAND
    _base_state = {"b": None}

    @property
    def binding_site(self):
        """
        Return the binding site for this ligand.

        Returns
        -------
        str
            The name of the binding site.
        """
        return self._sites[0]

    def binds_to(
        self,
        receptor: "Receptor",
        r_site: str,
        k_f: float | Parameter,
        k_r: float | Parameter,
        compartment: None | Compartment = None,
    ):
        """
        Create a reversible binding reaction between this ligand and a receptor.

        Parameters
        ----------
        receptor : Receptor
            The receptor to bind.
        r_site : str
            The binding site on the receptor.
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
        return self.binds(
            self.binding_site, receptor, r_site, k_f, k_r, compartment=compartment
        )

    def concertedly_activates(self, receptor, k_f, k_r, compartment=None):
        """
        Create a concerted activation reaction for a receptor by this ligand.

        Parameters
        ----------
        receptor : Receptor
            The receptor to activate.
        k_f : float or Parameter
            Forward rate constant.
        k_r : float or Parameter
            Reverse rate constant.
        compartment : Compartment or None, optional
            Compartment for the reaction (default: None).

        Returns
        -------
        ComponentSet
            PySB ComponentSet for the concerted activation reaction.
        """
        return receptor.concertedly_activated_by(self, k_f, k_r, compartment)


class Receptor(BindMixin, TurnoverMixin, FunctionalMonomer):
    """
    Class representing a receptor monomer with orthosteric/allosteric binding and activation.
    """

    _sites = ["b_ortho", "b_allo", "active"]
    _site_states = {"active": [False, True]}
    _functional_tag = PROTEIN.RECEPTOR
    _base_state = {"b_ortho": None, "b_allo": None, "active": False}
    _inactive_state = {"active": False}
    _active_state = {"active": True}

    @property
    def binding_sites(self):
        """
        Return the orthosteric and allosteric binding sites.

        Returns
        -------
        list
            List of binding site names.
        """
        return self._sites[:2]

    @property
    def orthosteric_site(self):
        """
        Return the orthosteric binding site.

        Returns
        -------
        str
            Name of the orthosteric site.
        """
        return self._sites[0]

    @property
    def allosteric_site(self):
        """
        Return the allosteric binding site.

        Returns
        -------
        str
            Name of the allosteric site.
        """
        return self._sites[1]

    @property
    def inactive(self):
        """
        Return the inactive state dictionary.

        Returns
        -------
        dict
            Dictionary representing the inactive state.
        """
        return self._inactive_state

    @property
    def active(self):
        """
        Return the active state dictionary.

        Returns
        -------
        dict
            Dictionary representing the active state.
        """
        return self._active_state

    def _binds_orthosteric(
        self,
        ligand: Ligand,
        k_f: float | Parameter,
        k_r: float | Parameter,
        compartment: None | Compartment = None,
    ):
        """
        Create a reversible binding reaction at the orthosteric site.

        Parameters
        ----------
        ligand : Ligand
            The ligand to bind.
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
        return self.binds(
            self.orthosteric_site,
            ligand,
            ligand.binding_site,
            k_f,
            k_r,
            compartment=compartment,
        )

    def _binds_allosteric(self, ligand: Ligand, k_f, k_r, compartment=None):
        """
        Create a reversible binding reaction at the allosteric site.

        Parameters
        ----------
        ligand : Ligand
            The ligand to bind.
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
        return self.binds(
            self.allosteric_site,
            ligand,
            ligand.binding_site,
            k_f,
            k_r,
            compartment=compartment,
        )

    def bound_by(self, ligand, k_f, k_r, location="orthosteric", compartment=None):
        """
        Create a reversible binding reaction at the specified site.

        Parameters
        ----------
        ligand : Ligand
            The ligand to bind.
        k_f : float or Parameter
            Forward rate constant.
        k_r : float or Parameter
            Reverse rate constant.
        location : str, optional
            "orthosteric" or "allosteric" (default: "orthosteric").
        compartment : Compartment or None, optional
            Compartment for the reaction (default: None).

        Returns
        -------
        ComponentSet
            PySB ComponentSet for the binding reaction.
        """
        if location == "orthosteric":
            return self._binds_orthosteric(ligand, k_f, k_r, compartment=compartment)
        elif location == "allosteric":
            return self._binds_allosteric(ligand, k_f, k_r, compartment=compartment)

    def concertedly_activated_by(self, ligand: Ligand, k_f, k_r, compartment=None):
        """
        Create a concerted activation reaction for this receptor by a ligand.

        Parameters
        ----------
        ligand : Ligand
            The ligand to activate this receptor.
        k_f : float or Parameter
            Forward rate constant.
        k_r : float or Parameter
            Reverse rate constant.
        compartment : Compartment or None, optional
            Compartment for the reaction (default: None).

        Returns
        -------
        ComponentSet
            PySB ComponentSet for the concerted activation reaction.
        """
        return activate_concerted(
            ligand,
            ligand.binding_site,
            self,
            self.orthosteric_site,
            self.inactive,
            self.active,
            [k_f, k_r],
            compartment=compartment,
        )
