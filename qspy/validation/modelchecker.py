"""
QSPy ModelChecker Utilities
===========================

This module provides the ModelChecker class for validating PySB/QSPy models.
It checks for unused or zero-valued parameters, unused monomers, missing initial
conditions, dangling bonds, unit consistency, and other common modeling issues.
Warnings are logged and also issued as Python warnings for user visibility.

Classes
-------
ModelChecker : Performs a suite of checks on a PySB/QSPy model for common issues.

Examples
--------
>>> checker = ModelChecker(model)
>>> checker.check()
"""

import logging
import warnings

import numpy as np

from pysb.core import SelfExporter, MonomerPattern
from pysb.pattern import (
    check_dangling_bonds,
    monomers_from_pattern,
    SpeciesPatternMatcher,
    RulePatternMatcher,
    ReactionPatternMatcher,
)
from pysb.bng import generate_equations
from pysb.units.core import check as units_check

from qspy.core import Monomer, Parameter
from qspy.utils.logging import ensure_qspy_logging, log_event
from qspy.config import LOGGER_NAME

warnings.simplefilter("always", UserWarning)  # Always show UserWarnings


class ModelChecker:
    """
    Performs a suite of checks on a PySB/QSPy model for common modeling issues.

    Checks include:
    - Unused monomers
    - Unused parameters
    - Zero-valued parameters
    - Missing initial conditions
    - Dangling/reused bonds
    - Unit consistency
    - (Optional) unbound sites, overdefined rules, unreferenced expressions

    Parameters
    ----------
    model : pysb.Model, optional
        The model to check. If None, uses the current SelfExporter.default_model.
    logger_name : str, optional
        Name of the logger to use (default: LOGGER_NAME).

    Attributes
    ----------
    model : pysb.Model
        The model being checked.
    logger : logging.Logger
        Logger for outputting warnings and info.
    """

    def __init__(self, model=None, logger_name=LOGGER_NAME):
        """
        Initialize the ModelChecker.

        Parameters
        ----------
        model : pysb.Model, optional
            The model to check. If None, uses the current SelfExporter.default_model.
        logger_name : str, optional
            Name of the logger to use.
        """
        self.model = model
        if model is None:
            self.model = SelfExporter.default_model
        ensure_qspy_logging()
        self.logger = logging.getLogger(logger_name)
        self.check()

    @log_event()
    def check(self):
        """
        Run all model checks.

        Returns
        -------
        None
        """
        self.logger.info("🔍 Running ModelChecker...")
        self.check_unused_monomers()
        self.check_unused_parameters()
        self.check_zero_valued_parameters()
        self.check_missing_initial_conditions()
        # self.check_unconnected_species()
        # self.check_unbound_sites()
        # self.check_overdefined_rules()
        # self.check_unreferenced_expressions()
        # units_check(self.model)
        self.check_dangling_reused_bonds()
        self.check_units()
        self.check_equations_generation()
        self.logger.info("✅ ModelChecker checks completed.")

    def check_unused_monomers(self):
        """
        Check for monomers that are not used in any rules.

        Logs and warns about unused monomers.

        Returns
        -------
        None
        """
        used = set()
        for rule in self.model.rules:
            used.update(
                m.name
                for m in monomers_from_pattern(rule.rule_expression.reactant_pattern)
            )
            # monomers_from_pattern doesn't handle None, so we need to
            # check here or it will cause a problem with the set.union method.
            if rule.is_reversible:
                used.update(
                    m.name
                    for m in monomers_from_pattern(rule.rule_expression.product_pattern)
                )

        unused = [m.name for m in self.model.monomers if m.name not in used]
        if len(unused) > 0:
            msg = f"Unused Monomers (not included in any Rules): {[m for m in unused]}"
            self.logger.warning(f"⚠️ {msg}")
            warnings.warn(msg, category=UserWarning)
            print(f"⚠️ {msg}")  # Print to console for visibility

    def check_unused_parameters(self):
        """
        Check for parameters that are not used in rules, initials, or expressions.

        Logs and warns about unused parameters.

        Returns
        -------
        None
        """
        used = set()
        for rule in self.model.rules:
            if isinstance(rule.rate_forward, Parameter):
                used.add(rule.rate_forward.name)
            if rule.is_reversible:
                if isinstance(rule.rate_reverse, Parameter):
                    used.add(rule.rate_reverse.name)
        for ic in self.model.initials:
            if isinstance(ic.value, Parameter):
                used.add(ic.value.name)
        for expr in self.model.expressions:
            used.update(p.name for p in expr.expr.atoms(Parameter))
        for compartment in self.model.compartments:
            if isinstance(compartment.size, Parameter):
                used.add(compartment.size.name)

        unused = [p.name for p in self.model.parameters if p.name not in used]
        if unused:
            msg = f"Unused Parameters: {[p for p in unused]}"
            self.logger.warning(f"⚠️ {msg}")
            warnings.warn(msg, category=UserWarning)
            print(f"⚠️ {msg}")  # Print to console for visibility

    def check_zero_valued_parameters(self):
        """
        Check for parameters with a value of zero.

        Logs and warns about zero-valued parameters.

        Returns
        -------
        None
        """
        zeros = [p for p in self.model.parameters if np.isclose(p.value, 0.0)]
        if zeros:
            msg = f"Zero-valued Parameters: {[p.name for p in zeros]}"
            self.logger.warning(f"⚠️ {msg}")
            warnings.warn(msg, category=UserWarning)
            print(f"⚠️ {msg}")  # Print to console for visibility

    def check_missing_initial_conditions(self):
        """
        Check for monomers missing initial conditions.

        Logs and warns about monomers that do not have initial conditions defined.

        Returns
        -------
        None
        """
        defined = list()
        for initial in self.model.initials:
            for m in monomers_from_pattern(initial.pattern):
                defined.append(m.name)
        defined = set(defined)
        all_monomers = set(m.name for m in self.model.monomers)
        missing = all_monomers - defined
        if missing:
            msg = f"Monomers missing initial conditions: {list(missing)}"
            self.logger.warning(f"⚠️ {msg}")
            warnings.warn(msg, category=UserWarning)
            print(f"⚠️ {msg}")  # Print to console for visibility

    def check_dangling_reused_bonds(self):
        """
        Check for dangling or reused bonds in all rules.

        Returns
        -------
        None
        """
        for rule in self.model.rules:
            try:
                check_dangling_bonds(rule.rule_expression.reactant_pattern)
            except Exception as e:
                msg = f"Error checking reactant pattern in rule '{rule.name}': {e}"
                self.logger.error(msg)
                warnings.warn(msg, category=UserWarning)
                print(msg)  # Print to console for visibility
            if rule.is_reversible:
                try:
                    check_dangling_bonds(rule.rule_expression.product_pattern)
                except Exception as e:
                    msg = f"Error checking product pattern in rule '{rule.name}': {e}"
                    self.logger.error(msg)
                    warnings.warn(msg, category=UserWarning)
                    print(msg)  # Print to console for visibility

    def check_equations_generation(self):
        """
        Run the `generate_equations` function on the model and capture and report any errors.

        Returns
        -------
        None
        """
        try:
            generate_equations(self.model)
            self.logger.info("Model equations generated successfully.")
        except Exception as e:
            msg = f"Error generating model equations: {e}"
            self.logger.error(msg)
            warnings.warn(msg, category=UserWarning)
            print(msg)  # Print to console for visibility

    @log_event()
    def check_units(self):
        """
        Check for unit consistency in the model.

        Returns
        -------
        None
        """
        units_check(self.model)

    def check_unbound_sites(self):
        """
        Check for sites that never participate in bonds.

        Logs and warns about unbound sites.

        Returns
        -------
        None
        """
        bound_sites = set()
        for r in self.model.rules:
            for cp in r.rule_expression().all_complex_patterns():
                for m in cp.monomer_patterns:
                    for site, state in m.site_conditions.items():
                        if isinstance(state, tuple):  # bond tuple
                            bound_sites.add((m.monomer.name, site))

        unbound = []
        for m in self.model.monomers:
            for site in m.sites:
                if (m.name, site) not in bound_sites:
                    unbound.append(f"{m.name}.{site}")

        if unbound:
            msg = f"Unbound Sites (never participate in bonds): {unbound}"
            self.logger.warning(f"⚠️ {msg}")
            warnings.warn(msg, category=UserWarning)

    def check_overdefined_rules(self):
        """
        Check for rules that define the same reaction more than once.

        Logs and warns about overdefined rules.

        Returns
        -------
        None
        """
        seen = {}
        for r in self.model.rules:
            rxn = str(r.rule_expression())
            if rxn in seen:
                msg = f"Overdefined reaction: '{rxn}' in rules `{seen[rxn]}` and `{r.name}`"
                self.logger.warning(f"⚠️ {msg}")
                warnings.warn(msg, category=UserWarning)
            else:
                seen[rxn] = r.name

    def check_unreferenced_expressions(self):
        """
        Check for expressions that are not referenced by any rule or observable.

        Logs and warns about unreferenced expressions.

        Returns
        -------
        None
        """
        used = set()
        for rule in self.model.rules:
            if rule.rate_forward:
                used.update(str(p) for p in rule.rate_forward.parameters)
            if rule.rate_reverse:
                used.update(str(p) for p in rule.rate_reverse.parameters)
        for o in self.model.observables:
            used.update(str(p) for p in o.function.atoms(Parameter))

        exprs = [e.name for e in self.model.expressions if e.name not in used]
        if exprs:
            msg = f"Unreferenced Expressions: {exprs}"
            self.logger.warning(f"⚠️ {msg}")
            warnings.warn(msg, category=UserWarning)
