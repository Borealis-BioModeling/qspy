"""
Functional monomer macros for QSPy experimental API.

Provides:
- activate_concerted: macro for concerted activation of a receptor by a ligand.
"""

from pysb import Monomer, Parameter, Expression, Observable, Compartment, Initial
from pysb.core import ComponentSet, as_complex_pattern, MonomerPattern, ComplexPattern
from pysb.macros import _macro_rule, _verify_sites, _complex_pattern_label
from pysb.pkpd.macros import _check_for_monomer


def activate_concerted(
    ligand: Monomer | MonomerPattern,
    l_site: str,
    receptor: Monomer | MonomerPattern,
    r_site: str,
    inactive_state: dict,
    active_state: dict,
    k_list: list,
    compartment: None | Compartment = None,
):
    """
    Generate a concerted activation reaction for a receptor by a ligand.

    This macro creates a reversible binding rule where a ligand binds to a receptor,
    and the receptor transitions from an inactive state to an active state as part of the binding event.

    Parameters
    ----------
    ligand : Monomer or MonomerPattern
        The ligand species or pattern.
    l_site : str
        The binding site on the ligand.
    receptor : Monomer or MonomerPattern
        The receptor species or pattern.
    r_site : str
        The binding site on the receptor.
    inactive_state : dict
        Dictionary specifying the inactive state of the receptor.
    active_state : dict
        Dictionary specifying the active state of the receptor.
    k_list : list
        List of rate constants [k_f, k_r] for forward and reverse reactions.
    compartment : Compartment or None, optional
        The compartment in which the reaction occurs (default: None).

    Returns
    -------
    ComponentSet
        The generated components, including the reversible activation Rule.

    Examples
    --------
    Concerted activation of a receptor by a ligand::

        Model()
        Monomer('Ligand', ['b'])
        Monomer('Receptor', ['b', 'state'], {'state': ['inactive', 'active']})
        activate_concerted(
            Ligand, 'b', Receptor, 'b',
            {'state': 'inactive'}, {'state': 'active'},
            [1e-3, 1e-3]
        )

    """
    _verify_sites(ligand, l_site)
    _verify_sites(receptor, [r_site] + list(active_state.keys()))
    def activate_concerted_name_func(rule_expression):
        cps = rule_expression.reactant_pattern.complex_patterns
        if compartment is not None:
            comp_name = compartment.name
            return "_".join(_complex_pattern_label(cp) for cp in cps).join(
                ["_", comp_name]
            )
        else:
            return "_".join(_complex_pattern_label(cp) for cp in cps)

    s1_free = ligand(**{l_site: None})
    s1_bound = ligand(**{l_site: 1})
    s2_i = receptor(**{r_site: None}.update(inactive_state))
    s2_a = receptor(**{r_site: 1}.update(active_state))
    if compartment is not None:
        s1_free = _check_for_monomer(s1_free, compartment)
        s1_bound = _check_for_monomer(s1_bound, compartment)
        s2_i = _check_for_monomer(s2_i, compartment)
        s2_a = _check_for_monomer(s2_a, compartment)

    return _macro_rule(
        "activate_concerted",
        s1_free + s2_i | s1_bound % s2_a,
        k_list,
        ["k_f", "k_r"],
        name_func=activate_concerted_name_func,
    )
