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

from qspy.base import ComponentContext
from qspy.core import Monomer, Parameter, Expression, Rule, Compartment
from qspy.config import LOGGER_NAME
from qspy.utils.logging import log_event
from qspy.base import SKIP_TYPES

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
        if isinstance(val, sympy.Expr):
            return (val, None)
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
        if isinstance(value, sympy.Expr):
            expr = Expression(name, value)
            return expr
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
    def _validate_value(name, size):
        """
        Validate the size for a compartment.

        Parameters
        ----------
        name : str
            Name of the compartment.
        size : Parameter or Expression
            Size of the compartment.

        Returns
        -------
        tuple
            (size,)

        Raises
        ------
        ValueError
            If the size is not a Parameter or Expression.
        """
        if not isinstance(size, (Parameter, Expression)):
            raise ValueError(
                f"Compartment size for '{name}' must be a Parameter or constant expression"
            )
        return (size,)

    @log_event(log_args=True, log_result=True, static_method=True)
    @staticmethod
    def create_component(name, size):
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
        compartment = Compartment(name, size=size)
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
        if not isinstance(val, tuple) or (len(val) not in [2, 3]):
            raise ValueError(
                f"Context-defined Monomer '{name}' must be a tuple: (sites, site_states) OR (sites, site_states, functional_tag)"
            )
        if len(val) == 2:
            sites, site_states = val
            functional_tag = None
        if len(val) == 3:
            sites, site_states, functional_tag = val
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
        if functional_tag is None:
            monomer = Monomer(name, sites, site_states)
        else:
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
        if not isinstance(val, tuple) or (len(val) < 2 or len(val) > 3):
            raise ValueError(
                f"Rule '{name}' input must be a tuple: (RuleExpression, rate_forward) if irreversible or (RuleExpression, rate_forward, rate_reverse) if reversible"
            )
        if len(val) == 2:
            rxp, rate_forward = val
            rate_reverse = None
        elif len(val) == 3:
            rxp, rate_forward, rate_reverse = val
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
        rule = Rule(name, rxp, rate_forward, rate_reverse)
        return rule


from contextlib import contextmanager


@contextmanager
def initials():
    """
    Context manager for defining initial conditions in a QSPy model.

    Yields
    ------
    None
    """
    try:
        yield
    finally:
        pass


@contextmanager
def observables():
    """
    Context manager for defining observables in a QSPy model.

    Yields
    ------
    None
    """
    try:
        yield
    finally:
        pass


class pk_macros:
    """
    Context manager stub for PK macros (pharmacokinetic macros).

    This is a placeholder for future PK macro context management.
    """

    def __enter__(self):
        """
        Enter the PK macros context.

        Returns
        -------
        pk_macros
            The context manager instance.
        """

        def noop(*args):
            pass

        self.eliminate = noop
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Exit the PK macros context and perform cleanup.

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
        print("Exiting context: cleaning up special_function")
        f_locals = inspect.currentframe().f_back.f_locals
        for key in f_locals:
            print(key)
