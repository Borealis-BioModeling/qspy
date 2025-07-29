"""
QSPy experimental infix macros for expressive model syntax.

Provides infix-style macro objects for binding, elimination, and equilibrium interactions:
- binds: infix macro for reversible binding reactions
- eliminated: infix macro for elimination reactions
- equilibrates: infix macro for reversible state transitions

These macros enable expressive model code such as:
    species *binds* target & (k_f, k_r)
    species *eliminated* compartment & k_deg
    state1 *equilibrates* state2 & (k_f, k_r)
"""

from abc import ABC, abstractmethod

from qspy.core import Monomer, Parameter
from pysb.core import MonomerPattern, ComplexPattern, Compartment, ComponentSet
from pysb.macros import bind, equilibrate
from pysb.pkpd.macros import eliminate


class InfixMacro(ABC):
    """
    Abstract base class for infix-style macros in QSPy.

    This class provides a structure for creating infix-style macros that can be used
    in a way that more closely resembles specifying a biological action.
    Adapted from `Infix` class example at: https://discuss.python.org/t/infix-function-in-python/41820/2
    """

    def __init__(self, lhs=None, rhs=None):
        """
        Initialize the infix macro with optional left and right sides.

        Parameters
        ----------
        lhs : any, optional
            The left-hand side of the infix operation.
        rhs : any, optional
            The right-hand side of the infix operation.
        """
        self.lhs = lhs
        self.rhs = rhs

    @abstractmethod
    def execute_macro(self, lhs, rhs, at):
        """
        Abstract method to execute the macro logic.

        Parameters
        ----------
        lhs : any
            The left-hand side operand.
        rhs : any
            The right-hand side operand.
        at : any
            Additional argument for the macro.

        Returns
        -------
        any
            The result of the macro operation.
        """
        pass

    def __rmul__(self, lhs):
        """
        Capture the left-hand side operand for the infix macro.

        Parameters
        ----------
        lhs : any
            The left-hand side operand.

        Returns
        -------
        InfixMacro
            The same instance with lhs set.
        """
        self.lhs = lhs
        return self

    def __mul__(self, rhs):
        """
        Capture the right-hand side operand for the infix macro.

        Parameters
        ----------
        rhs : any
            The right-hand side operand.

        Returns
        -------
        InfixMacro
            The same instance with rhs set.
        """
        self.rhs = rhs
        return self

    def __and__(self, at):
        """
        Execute the macro logic using the & operator.

        Parameters
        ----------
        at : any
            Additional argument for the macro.

        Returns
        -------
        any
            The result of the macro operation.
        """
        return self.execute_macro(self.lhs, self.rhs, at)

    @staticmethod
    def parse_pattern(pattern: MonomerPattern | ComplexPattern):
        """
        Parse the monomer pattern to extract relevant information.

        Parameters
        ----------
        pattern : MonomerPattern or ComplexPattern
            The pattern to parse.

        Returns
        -------
        tuple
            A tuple containing the monomer, binding site, state, and compartment.
        """
        mono = pattern.monomer
        bsite = next(
            (key for key, value in pattern.site_conditions.items() if value is None),
            None,
        )
        state = {
            key: value for key, value in pattern.site_conditions.items() if key != bsite
        }
        compartment = pattern.compartment
        return mono, bsite, state, compartment


class _Binds(InfixMacro):
    def __rmul__(self, lhs: MonomerPattern | ComplexPattern):
        """
        Capture the left-hand side monomer or complex pattern.

        Parameters
        ----------
        other : MonomerPattern or ComplexPattern
            The left-hand side of the infix operation.

        Returns
        -------
        binds
            Returns self to allow chaining with the right-hand side.
        """
        if not isinstance(lhs, (MonomerPattern, ComplexPattern)):
            return NotImplemented
        self.lhs = lhs
        return self  # Return an instance to allow chaining with the right-hand side

    def __mul__(self, rhs: MonomerPattern | ComplexPattern):
        """
        Capture the right-hand side monomer or complex pattern and create the binding rule.

        Parameters
        ----------
        other : MonomerPattern or ComplexPattern
            The right-hand side of the infix operation.

        Returns
        -------
        ComponentSet
            The PySB ComponentSet from the corresponding call to the bind macro.
        """
        if not isinstance(rhs, (MonomerPattern, ComplexPattern)):
            return NotImplemented
        self.rhs = rhs
        return self

    def __matmul__(self, at: tuple[str] | list[str]):
        """
        Capture the additional argument for the macro using the @ operator.

        Parameters
        ----------
        at : tuple[str] | list[str]
            The additional argument for the macro.

        Returns
        -------
        InfixMacro
            The same instance with at set.
        """
        lb, rb = at
        lhs_sites = {lb: None}
        lhs_sites |= self.lhs.site_conditions
        rhs_sites = {rb: None}
        rhs_sites |= self.rhs.site_conditions
        self.lhs = self.lhs.monomer(**lhs_sites) ** self.lhs.compartment
        self.rhs = self.rhs.monomer(**rhs_sites) ** self.rhs.compartment
        return self

    def __and__(
        self, _and: tuple[float | Parameter] | list[float | Parameter]
    ) -> ComponentSet:
        """
        Execute the binding macro using the & operator.

        Parameters
        ----------
        at : tuple[float] | tuple[Parameter]
            Additional arguments for the macro.

        Returns
        -------
        ComponentSet
            The PySB ComponentSet from the corresponding call to the bind macro.
        """
        if self.lhs is None or self.rhs is None:
            return NotImplemented
        if not isinstance(_and, (tuple, list)):
            return NotImplemented
        if not len(_and) == 2:
            raise ValueError("Must be a two-element tuple of form (k_f, k_r)")
        return self.execute_macro(self.lhs, self.rhs, [*_and])

    def execute_macro(
        self,
        lhs: MonomerPattern | ComplexPattern,
        rhs: MonomerPattern | ComplexPattern,
        at: tuple[Parameter, Parameter],
    ) -> ComponentSet:
        """
        Execute the binding macro logic.

        Parameters
        ----------
        lhs : MonomerPattern or ComplexPattern
            The left-hand side of the infix operation.
        rhs : MonomerPattern or ComplexPattern
            The right-hand side of the infix operation.
        at : tuple[Parameter, Parameter]
            A tuple containing the forward and reverse rate constants.

        Returns
        -------
        ComponentSet
            The PySB ComponentSet from the corresponding call to the bind macro.
        """
        k_f, k_r = at
        left_mono, left_bsite, left_state, left_compartment = self.parse_pattern(lhs)
        right_mono, right_bsite, right_state, right_compartment = self.parse_pattern(
            rhs
        )

        return bind(
            left_mono(**left_state) ** left_compartment,
            left_bsite,
            right_mono(**right_state) ** right_compartment,
            right_bsite,
            [k_f, k_r],
        )


class _Eliminated(InfixMacro):
    def __rmul__(self, lhs: MonomerPattern | ComplexPattern | Monomer):
        """
        Capture the left-hand side monomer or complex pattern for the elimination macro.

        Parameters
        ----------
        lhs : MonomerPattern or ComplexPattern
            The species to be eliminated from a compartment.

        Returns
        -------
        _EliminatedFrom
            The same instance with lhs set, allowing chaining with the right-hand side.
        """
        if not isinstance(lhs, (MonomerPattern, ComplexPattern, Monomer)):
            return NotImplemented
        self.lhs = lhs
        return self  # Return an instance to allow chaining with the right-hand side

    def __mul__(self, rhs: Compartment):
        """
        Capture the right-hand side compartment for the elimination macro.

        Parameters
        ----------
        rhs : Compartment
            The compartment from which the species will be eliminated.

        Returns
        -------
        _EliminatedFrom
            The same instance with rhs set, allowing chaining with the @ operator.
        """
        if not isinstance(rhs, Compartment):
            return NotImplemented
        self.rhs = rhs
        return self

    def execute_macro(
        self,
        lhs: MonomerPattern | ComplexPattern,
        rhs: Compartment,
        at: Parameter | float,
    ) -> ComponentSet:
        """
        Execute the elimination macro logic.

        Parameters
        ----------
        lhs : MonomerPattern or ComplexPattern
            The species to be eliminated.
        rhs : Compartment
            The compartment from which the species will be eliminated.
        at : Parameter or float
            The elimination rate constant.

        Returns
        -------
        ComponentSet
            The PySB ComponentSet from the corresponding call to the eliminate macro.
        """
        return eliminate(lhs, rhs, at)

    def __and__(self, at: Parameter | float) -> ComponentSet:
        """
        Execute the elimination macro using the & operator.

        Parameters
        ----------
        at : Parameter or float
            The elimination rate constant.

        Returns
        -------
        ComponentSet
            The PySB ComponentSet from the corresponding call to the eliminate macro.
        """
        if self.lhs is None or self.rhs is None:
            return NotImplemented

        return self.execute_macro(self.lhs, self.rhs, at)



class _Equilibrates(_Binds):
    """
    A class to represent an equilibrating two states.

    """

    def __matmul__(self, at):
        return self

    def execute_macro(
        self,
        lhs: MonomerPattern | ComplexPattern,
        rhs: MonomerPattern | ComplexPattern,
        _and: tuple[Parameter, Parameter],
    ) -> ComponentSet:
        """
        Execute the equilibrate macro logic.

        Parameters
        ----------
        lhs : MonomerPattern or ComplexPattern
            The left-hand side of the infix operation.
        rhs : MonomerPattern or ComplexPattern
            The right-hand side of the infix operation.
        _and : tuple[Parameter, Parameter]
            A tuple containing the forward and reverse rate constants.

        Returns
        -------
        ComponentSet
            The PySB ComponentSet from the corresponding call to the equilibrate macro.
        """
        k_f, k_r = _and
        return equilibrate(lhs, rhs, [k_f, k_r])



# Create instances of the infix macros
binds = _Binds()  # Create an instance of the binds infix macro
eliminated = _Eliminated()  # Create an instance of the eliminated infix macro
equilibrates = _Equilibrates()  # Create an instance of the equilibrates infix macro

__all__ = [
    "binds",  # The binds infix macro for binding interactions
    "eliminated",  # The eliminated infix macro for elimination interactions
    "equilibrates",  # The equilibrates infix macro for equilibrium interactions
]
