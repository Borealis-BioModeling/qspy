"""
QSPy Context Managers for Model Construction
============================================

This module provides context managers and utilities for structured, validated
construction of quantitative systems pharmacology (QSP) models using QSPy.
Each context manager encapsulates the logic for defining a specific model
component (parameters, compartments, monomers, expressions, rules, initials,
observables), ensuring type safety, unit checking, and extensibility.

Classes
-------
parameters   : Context manager for defining model parameters (numeric or symbolic).
compartments : Context manager for defining model compartments.
monomers     : Context manager for defining model monomers with optional functional tags.
expressions  : Context manager for defining model expressions (sympy-based).
rules        : Context manager for defining model rules (reversible/irreversible).
pk_macros    : Stub context manager for future pharmacokinetic macro support.

Functions
---------
initials()     : Context manager for defining initial conditions.
observables()  : Context manager for defining observables.

Examples
--------
>>> with parameters():
...     k1 = (1.0, "1/min")

>>> with monomers():
...     A = (["b"], {"b": ["u", "p"]})

>>> with rules():
...     bind = (A(b=None) + B(), kf, kr)
"""

import inspect
import sys
from contextlib import contextmanager
from enum import Enum

import sympy
import pysb
from pysb.units.core import check as units_check

from qspy.contexts.base import ComponentContext
from qspy.core import Monomer, Parameter, Expression, Rule, Compartment
from qspy.config import LOGGER_NAME
from qspy.utils.logging import log_event
from qspy.contexts.base import SKIP_TYPES

# from pysb.units import add_macro_units
# from pysb.pkpd import macros as pkpd
# from pysb.pkpd import macros as pkpd
# add_macro_units(pkpd)
# from pysb.pkpd.macros import eliminate, distribute

# add_macro_units(pkpd)

__all__ = [
    "parameters",
    "compartments",
    "monomers",
    "expressions",
    "rules",
    "initials",
    "observables",
    "macros",
    # "pk_macros",
    # "units",
]

# @contextmanager
# def units(concentration: str = "mg/L", time: str = "h", volume: str = 'L'):
#     try:
#         sim_units = core.SimulationUnits(concentration, time, volume)
#         yield sim_units
#     finally:
#         pass


class parameters(ComponentContext):
    """
    Context manager for defining model parameters in a QSPy model.

    Provides validation and creation logic for parameters, supporting both numeric
    and symbolic (sympy.Expr) values.

    Methods
    -------
    _validate_value(name, val)
        Validate the value and unit for a parameter.
    create_component(name, value, unit)
        Create a parameter or expression component.
    """

    component_name = "parameter"

    @staticmethod
    def _validate_value(name, val):
        """
        Validate the value and unit for a parameter.

        Parameters
        ----------
        name : str
            Name of the parameter.
        val : tuple
            Tuple of (value, unit).

        Returns
        -------
        tuple
            (value, unit) if valid.

        Raises
        ------
        ValueError
            If the value or unit is invalid.
        """
        # Accept sympy expressions directly as expressions
        if isinstance(val, sympy.Expr):
            return (val, None)
        # Ensure tuple structure for numeric parameters
        if not isinstance(val, tuple) or len(val) != 2:
            raise ValueError(f"Parameter '{name}' must be a tuple: (value, unit)")
        value, unit = val
        if not isinstance(value, (int, float)):
            raise ValueError(f"Parameter value for '{name}' must be a number")
        if not isinstance(unit, str):
            raise ValueError(f"Unit for parameter '{name}' must be a string")
        return (value, unit)

    @log_event(log_args=True, log_result=True, static_method=True)
    @staticmethod
    def create_component(name, value, unit):
        """
        Create a parameter or expression component.

        Parameters
        ----------
        name : str
            Name of the parameter.
        value : int, float, or sympy.Expr
            Value of the parameter or a sympy expression.
        unit : str or None
            Unit for the parameter.

        Returns
        -------
        Parameter or Expression
            The created parameter or expression.
        """
        # If value is a sympy expression, create an Expression
        if isinstance(value, sympy.Expr):
            expr = Expression(name, value)
            return expr
        # Otherwise, create a Parameter
        param = Parameter(name, value, unit=unit)
        return param

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Exit the parameter context and perform unit checking.

        Parameters
        ----------
        exc_type : type
            Exception type, if any.
        exc_val : Exception
            Exception value, if any.
        exc_tb : traceback
            Traceback, if any.

        Returns
        -------
        None
        """
        super().__exit__(exc_type, exc_val, exc_tb)
        # Check units for all parameters in the model
        units_check(self.model)
        return


class compartments(ComponentContext):
    """
    Context manager for defining model compartments in a QSPy model.

    Provides validation and creation logic for compartments.

    Methods
    -------
    _validate_value(name, size)
        Validate the size for a compartment.
    create_component(name, size)
        Create a compartment component.
    """

    component_name = "compartment"

    @staticmethod
    def _validate_value(name, val):
        """
        Validate the size for a compartment.

        Parameters
        ----------
        name : str
            Name of the compartment.
        val : tuple | Parameter | Expression
            Tuple of (size, dimensions) or Parameter/Expression for size.

        Returns
        -------
        tuple
            (size, dimensions)

        Raises
        ------
        ValueError
            If the size is not a Parameter or Expression.
        """
        if not isinstance(val, (tuple, Parameter, Expression)):
            raise ValueError(
                f"Compartment '{name}' must be a tuple: (size, dimensions) or a Parameter/Expression for size"
            )
        if isinstance(val, tuple):
            if len(val) != 2:
                raise ValueError(
                    f"Compartment '{name}' tuple must be of the form (size, dimensions)"
                )
            size, dimensions = val
            if not isinstance(size, (Parameter, Expression)):
                raise ValueError(
                    f"Compartment size for '{name}' must be a Parameter or Expression"
                )
            if not isinstance(dimensions, int):
                raise ValueError(
                    f"Compartment dimensions for '{name}' must be an integer"
                )
        else:
            size = val
            dimensions = 3  # Default to 3D if not specified
        return (size, dimensions)

    @log_event(log_args=True, log_result=True, static_method=True)
    @staticmethod
    def create_component(name, size, dimensions):
        """
        Create a compartment component.

        Parameters
        ----------
        name : str
            Name of the compartment.
        size : Parameter or Expression
            Size of the compartment.

        Returns
        -------
        Compartment
            The created compartment.
        """
        compartment = Compartment(name, size=size, dimension=dimensions)
        return compartment


class monomers(ComponentContext):
    """
    Context manager for defining model monomers in a QSPy model.

    Provides validation and creation logic for monomers, including optional functional tags.

    Methods
    -------
    _validate_value(name, val)
        Validate the tuple for monomer definition.
    create_component(name, sites, site_states, functional_tag)
        Create a monomer component.
    """

    component_name = "monomer"

    @staticmethod
    def _validate_value(name, val):
        """
        Validate the tuple for monomer definition.

        Parameters
        ----------
        name : str
            Name of the monomer.
        val : tuple
            Tuple of (sites, site_states) or (sites, site_states, functional_tag).

        Returns
        -------
        tuple
            (sites, site_states, functional_tag)

        Raises
        ------
        ValueError
            If the tuple is not valid.
        """
        # Accept either (sites, site_states) or (sites, site_states, functional_tag)
        if not isinstance(val, tuple) or (len(val) not in [2, 3]):
            raise ValueError(
                f"Context-defined Monomer '{name}' must be a tuple: (sites, site_states) OR (sites, site_states, functional_tag)"
            )
        if len(val) == 2:
            sites, site_states = val
            functional_tag = None
        if len(val) == 3:
            sites, site_states, functional_tag = val
        # Validate types for each field
        if (sites is not None) and (not isinstance(sites, list)):
            raise ValueError(
                f"Monomer sites value for '{name}' must be a list of site names"
            )
        if (site_states is not None) and (not isinstance(site_states, dict)):
            raise ValueError(
                f"Monomer site_states for '{name}' must be a dictionary of sites and their states"
            )
        if (functional_tag is not None) and (not isinstance(functional_tag, Enum)):
            raise ValueError(
                f"Monomer functional tag for '{name} must be an Enum item'"
            )
        return (sites, site_states, functional_tag)

    @log_event(log_args=True, log_result=True, static_method=True)
    @staticmethod
    def create_component(name, sites, site_states, functional_tag):
        """
        Create a monomer component.

        Parameters
        ----------
        name : str
            Name of the monomer.
        sites : list
            List of site names.
        site_states : dict
            Dictionary of site states.
        functional_tag : Enum or None
            Functional tag for the monomer.

        Returns
        -------
        core.Monomer
            The created monomer.
        """
        # If no functional tag, create a plain Monomer
        if functional_tag is None:
            monomer = Monomer(name, sites, site_states)
        else:
            # If functional tag is provided, attach it
            monomer = Monomer(name, sites, site_states) @ functional_tag
        return monomer


class expressions(ComponentContext):
    """
    Context manager for defining model expressions in a QSPy model.

    Provides validation and creation logic for expressions.

    Methods
    -------
    _validate_value(name, val)
        Validate the value for an expression.
    create_component(name, expr)
        Create an expression component.
    """

    component_name = "expression"

    @staticmethod
    def _validate_value(name, val):
        """
        Validate the value for an expression.

        Parameters
        ----------
        name : str
            Name of the expression.
        val : sympy.Expr
            The sympy expression.

        Returns
        -------
        tuple
            (val,)

        Raises
        ------
        ValueError
            If the value is not a sympy.Expr.
        """
        # Only allow sympy expressions for expressions
        if not isinstance(val, sympy.Expr):
            raise ValueError(f"Expression '{name}' must be a sympy.Expr")
        return (val,)

    @log_event(log_args=True, log_result=True, static_method=True)
    @staticmethod
    def create_component(name, expr):
        """
        Create an expression component.

        Parameters
        ----------
        name : str
            Name of the expression.
        expr : sympy.Expr
            The sympy expression.

        Returns
        -------
        Expression
            The created expression.
        """
        expression = Expression(name, expr)
        return expression


class rules(ComponentContext):
    """
    Context manager for defining model rules in a QSPy model.

    Provides validation and creation logic for rules, supporting both reversible and irreversible forms.

    Methods
    -------
    _validate_value(name, val)
        Validate the tuple for rule definition.
    create_component(name, rxp, rate_forward, rate_reverse)
        Create a rule component.
    """

    component_name = "rule"

    @staticmethod
    def _validate_value(name, val):
        """
        Validate the tuple for rule definition.

        Parameters
        ----------
        name : str
            Name of the rule.
        val : tuple
            Tuple of (RuleExpression, rate_forward) or (RuleExpression, rate_forward, rate_reverse).

        Returns
        -------
        tuple
            (rxp, rate_forward, rate_reverse)

        Raises
        ------
        ValueError
            If the tuple is not valid or contains invalid types.
        """
        # Accept either (RuleExpression, rate_forward) or (RuleExpression, rate_forward, rate_reverse)
        if not isinstance(val, tuple) or (len(val) < 2 or len(val) > 3):
            raise ValueError(
                f"Rule '{name}' input must be a tuple: (RuleExpression, rate_forward) if irreversible or (RuleExpression, rate_forward, rate_reverse) if reversible"
            )
        if len(val) == 2:
            rxp, rate_forward = val
            rate_reverse = None
        elif len(val) == 3:
            rxp, rate_forward, rate_reverse = val
        # Validate types for rule components
        if not isinstance(rxp, pysb.RuleExpression):
            raise ValueError(f"Rule '{name}' must contain a valid RuleExpression")
        if not isinstance(rate_forward, (Parameter, Expression)):
            raise ValueError(
                f"rate_forward value for '{name}' must be a Parameter or Expression"
            )
        if (rate_reverse is not None) and not isinstance(
            rate_forward, (Parameter, Expression)
        ):
            raise ValueError(
                f"rate_reverse value for '{name}' must be a Parameter or Expression"
            )
        return (rxp, rate_forward, rate_reverse)

    @log_event(log_args=True, log_result=True, static_method=True)
    @staticmethod
    def create_component(name, rxp, rate_forward, rate_reverse):
        """
        Create a rule component.

        Parameters
        ----------
        name : str
            Name of the rule.
        rxp : pysb.RuleExpression
            The rule expression.
        rate_forward : Parameter or Expression
            Forward rate parameter or expression.
        rate_reverse : Parameter or Expression or None
            Reverse rate parameter or expression (if reversible).

        Returns
        -------
        Rule
            The created rule.
        """
        # Create a Rule object with the provided arguments
        rule = Rule(name, rxp, rate_forward, rate_reverse)
        return rule


from contextlib import contextmanager


@contextmanager
def initials():
    """
    Context manager for defining initial conditions in a QSPy model.

    Tracks which initials are added within the context and logs them.

    Yields
    ------
    None
    """
    import logging
    from pysb.core import SelfExporter
    from qspy.config import LOGGER_NAME
    from qspy.utils.logging import ensure_qspy_logging

    ensure_qspy_logging()
    logger = logging.getLogger(LOGGER_NAME)
    model = SelfExporter.default_model

    # Record the set of initial names before entering the context
    initials_before = set(str(init.pattern) for init in model.initials)
    logger.info("[QSPy] Entering initials context manager")
    try:
        yield
    finally:
        # Record the set of initial names after exiting the context
        initials_after = set(str(init.pattern) for init in model.initials)
        added = initials_after - initials_before
        if added:
            # Log the names of newly added initials
            added_initials = [
                init for init in model.initials if str(init.pattern) in added
            ]
            logger.info(f"[QSPy] Initials added in context: {added_initials}")
        else:
            logger.info("[QSPy] No new initials added")


@contextmanager
def observables():
    """
    Context manager for defining observables in a QSPy model.

    Yields
    ------
    None
    """
    import logging
    from pysb.core import SelfExporter
    from qspy.config import LOGGER_NAME
    from qspy.utils.logging import ensure_qspy_logging

    ensure_qspy_logging()
    logger = logging.getLogger(LOGGER_NAME)
    model = SelfExporter.default_model

    # Record the set of observable names before entering the context
    observables_before = set(obs.name for obs in model.observables)
    logger.info("[QSPy] Entering observables context manager")
    try:
        yield
    finally:
        # Record the set of observable names after exiting the context
        observables_after = set(init.name for init in model.observables)
        added = observables_after - observables_before
        if added:
            # Log the names of newly added observables
            added_observables = [obs for obs in model.observables if obs.name in added]
            logger.info(f"[QSPy] Observables added in context: {added_observables}")
        else:
            logger.info("[QSPy] No new observables added")


@contextmanager
def macros():
    """
    Context manager for managing macros in a QSPy model.

    Yields
    ------
    None
    """
    import logging
    from pysb.core import SelfExporter
    from qspy.config import LOGGER_NAME
    from qspy.utils.logging import ensure_qspy_logging

    ensure_qspy_logging()
    logger = logging.getLogger(LOGGER_NAME)
    model = SelfExporter.default_model

    componenents_before = set(model.components.keys())

    logger.info("[QSPy] Entering macros context manager")
    try:
        yield
    finally:
        components_after = set(model.components.keys())
        added = components_after - componenents_before
        if added:
            # Log the names of newly added components
            added_components = [comp for comp in model.components if comp.name in added]
            logger.info(f"[QSPy] Components added in context: {added_components}")
        else:
            logger.info("[QSPy] No new components added")
    return
