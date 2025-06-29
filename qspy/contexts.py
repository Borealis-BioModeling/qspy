import sys
import inspect
from contextlib import contextmanager
from enum import Enum
import sympy
import pysb
from base import ComponentContext
import core
from pysb.units.core import check as units_check
from utils.logging import log_event, LOGGER_NAME
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
    component_name = "parameter"

    @staticmethod
    def _validate_value(name, val):
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
        if isinstance(value, sympy.Expr):
            expr = core.Expression(name, value)
            return expr
        param = core.Parameter(name, value, unit=unit)
        return param

    # @log_context_entry_exit(track_attr="parameters")
    # def __enter__(self):
    #     self._override = True
    #     return super().__enter__()

    #@log_context_entry_exit(track_attr="parameters")
    def __exit__(self, exc_type, exc_val, exc_tb):
        super().__exit__(exc_type, exc_val, exc_tb)
        units_check(self.model)
        return


class compartments(ComponentContext):
    component_name = "compartment"

    @staticmethod
    def _validate_value(name, size):

        if not isinstance(size, (core.Parameter, core.Expression)):
            raise ValueError(
                f"Compartment size for '{name}' must be a Parameter or constant expression"
            )
        return (size,)

    @log_event(log_args=True, log_result=True, static_method=True)
    @staticmethod
    def create_component(name, size):
        # print(size)
        compartment = core.Compartment(name, size=size)
        return compartment


class monomers(ComponentContext):
    component_name = "monomer"

    @staticmethod
    def _validate_value(name, val):
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
        if functional_tag is None:
            monomer = core.Monomer(name, sites, site_states)
        else:
            monomer = core.Monomer(name, sites, site_states) @ functional_tag
        return monomer


class expressions(ComponentContext):
    component_name = "expression"

    @staticmethod
    def _validate_value(name, val):
        if not isinstance(val, sympy.Expr):
            raise ValueError(f"Expression '{name}' must be a sympy.Expr")
        return (val,)

    @log_event(log_args=True, log_result=True, static_method=True)
    @staticmethod
    def create_component(name, expr):
        expression = core.Expression(name, expr)
        return expression


class rules(ComponentContext):
    component_name = "rule"

    @staticmethod
    def _validate_value(name, val):
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
        if not isinstance(rate_forward, (core.Parameter, core.Expression)):
            raise ValueError(
                f"rate_forward value for '{name}' must be a Parameter or Expression"
            )
        if (rate_reverse is not None) and not isinstance(
            rate_forward, (core.Parameter, core.Expression)
        ):
            raise ValueError(
                f"rate_reverse value for '{name}' must be a Parameter or Expression"
            )
        return (rxp, rate_forward, rate_reverse)

    @log_event(log_args=True, log_result=True, static_method=True)
    @staticmethod
    def create_component(name, rxp, rate_forward, rate_reverse):
        rule = core.Rule(name, rxp, rate_forward, rate_reverse)
        return rule


@contextmanager
def initials():
    try:
        yield
    finally:
        pass

@contextmanager
def observables():
    try:
        yield
    finally:
        pass

# @contextmanager
# def pk():
#     try:
#         from pysb.pkpd import macros as pkpd
#         add_macro_units(pkpd)
#         from pysb.pkpd.macros import eliminate, distribute
#         local = inspect.currentframe().f_back.f_locals
#         local['eliminate'] = eliminate
#         yield
#     finally:
#         del sys.modules['pysb.pkpd']
#         #locals = inspect.currentframe().f_back.f_locals
#         #del locals['eliminate']
#         #print(sys.modules)


class pk_macros:
    def __enter__(self):
        # from pysb.pkpd import macros as pkpd
        # add_macro_units(pkpd)
        # from pysb.pkpd.macros import eliminate, distribute
        # self.eliminate = eliminate
        def noop(*args):
            pass

        self.eliminate = noop
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        print("Exiting context: cleaning up special_function")
        # del self.eliminate # This effectively removes it
        # del sys.modules['pysb.pkpd']
        # del sys.modules['pysb.pkpd.util']
        # print(sys.modules)
        # print("looking at sys.modules")
        # matches = []
        # for key in sys.modules:
        #     if key.startswith('pysb'):
        #         print(key)
        # print("-----------------")
        # for key in sys.modules:
        #     if key.startswith('pysb.simulator'):
        #         print(key)
        #         matches.append(key)
        # for key in matches:
        #     del sys.modules[key]
        # #del sys.modules['pysb.simulator']
        # print("----------")
        # print("looking at f_locals")
        f_locals = inspect.currentframe().f_back.f_locals
        # del f_locals['pk']
        for key in f_locals:
            print(key)
