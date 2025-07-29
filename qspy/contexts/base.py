"""
QSPy Base Context Infrastructure
===============================

This module provides the abstract base class for QSPy context managers, which
enable structured and validated construction of model components (parameters,
monomers, compartments, etc.) in a PySB/QSPy model. The ComponentContext class
handles introspection, variable tracking, and component injection for both
manual and automatic (module-level) usage.

Classes
-------
ComponentContext : Abstract base class for all QSPy context managers.

Examples
--------
>>> class MyContext(ComponentContext):
...     def create_component(self, name, *args):
...         # Custom creation logic
...         pass
...
>>> with MyContext():
...     my_param = (1.0, "1/min")
"""

import copy
import inspect
import logging
import weakref
from abc import ABC, abstractmethod
from types import ModuleType

from pysb.core import SelfExporter, ComponentSet

from qspy.config import LOGGER_NAME
from qspy.utils.logging import ensure_qspy_logging


# Types to skip during introspection
# These are typically PySB components or context objects that don't need to be tracked/deep
# copied.
SKIP_TYPES = (
    "Parameter",
    "Monomer",
    "Rule",
    "Compartment",
    "Observable",
    "Expression",
    "Initial",
    "ComponentContext",
    "parameters",
    "expressions",
    "compartments",
    "monomers",
    "initials",
    "rules",
    "observables",
    "Model",
    "model",
    "__name__",
    "__doc__",
    "__package__",
    "__file__",
    "__loader__",
    "__spec__",
    "__cached__",
    "__builtins__",
    "__version__",
    "__author__",
    "pytest",
    "pysb",
    "pysb.core",
    "pysb.macros",
    "pysb.pkpd.macros",
    "pysb.pkpd",
)

def is_module(obj):
    """
    Check if the object is a module.

    Parameters
    ----------
    obj : object
        The object to check.

    Returns
    -------
    bool
        True if the object is a module, False otherwise.
    """
    return isinstance(obj, ModuleType)

class ComponentContext(ABC):
    """
    Abstract base class for QSPy context managers.

    Handles variable introspection, manual and automatic component addition,
    and provides a template for context-managed model construction.

    Parameters
    ----------
    manual : bool, optional
        If True, enables manual mode for explicit component addition (default: False).
    verbose : bool, optional
        If True, prints verbose output during component addition (default: False).

    Attributes
    ----------
    component_name : str
        Name of the component type (e.g., 'parameter', 'monomer').
    model : pysb.Model
        The active PySB model instance.
    _manual_adds : list
        List of manually added components (used in manual mode).
    _frame : frame
        Reference to the caller's frame for introspection.
    _locals_before : dict
        Snapshot of local variables before entering the context.
    _override : bool
        If True, disables module-scope enforcement.

    Methods
    -------
    __enter__()
        Enter the context, track local variables, and enforce module scope.
    __exit__(exc_type, exc_val, exc_tb)
        Exit the context, detect new variables, validate, and add components.
    __call__(name, *args)
        Add a component manually (manual mode only).
    _add_component(name, *args)
        Validate and add a component to the model.
    _validate_value(name, val)
        Validate or transform the right-hand-side value (override in subclasses).
    create_component(name, *args)
        Abstract method to create a component (must be implemented in subclasses).
    add_component(component)
        Add the component to the model.
    """

    component_name = "component"  # e.g. 'parameter', 'monomer'

    def __init__(self, manual: bool = False, verbose: bool = False):
        """
        Initialize the context manager.

        Parameters
        ----------
        manual : bool, optional
            If True, enables manual mode for explicit component addition (default: False).
        verbose : bool, optional
            If True, prints verbose output during component addition (default: False).
        """
        self.manual = manual
        self.verbose = verbose
        self._manual_adds = []
        self._frame = None
        self._locals_before = None
        # self.components = ComponentSet()
        self.model = SelfExporter.default_model
        self._override = False

    def __enter__(self):
        """
        Enter the context manager.

        Tracks local variables for automatic detection of new assignments.
        Enforces module-level usage unless manual mode or override is enabled.

        Returns
        -------
        self or None
            Returns self in manual mode, otherwise None.

        Raises
        ------
        RuntimeError
            If no active model is found or used outside module scope.
        """
        ensure_qspy_logging()
        logger = logging.getLogger(LOGGER_NAME)
        try:
            logger.info(f"[QSPy] Entering context: {self.__class__.__name__}")
            if self.model is None:
                logger.error("No active model found. Did you instantiate a Model()?")
                raise RuntimeError(
                    "No active model found. Did you instantiate a Model()?"
                )

            if self._override:
                self._frame = inspect.currentframe().f_back.f_back
            else:
                self._frame = inspect.currentframe().f_back

            # Require module-level use for introspection mode
            if (
                (not self.manual)
                and (self._frame.f_globals is not self._frame.f_locals)
            ) and (not self._override):
                logger.error(
                    f"{self.__class__.__name__} must be used at module scope. "
                    f"Wrap model components in a module-level script."
                )
                raise RuntimeError(
                    f"{self.__class__.__name__} must be used at module scope. "
                    f"Wrap model components in a module-level script."
                )

            if not self.manual:
                # Filter out model components and context objects before deepcopy

                filtered_locals = {
                    k: v
                    for k, v in self._frame.f_locals.items()
                    if not ((hasattr(v, "__class__") and k in SKIP_TYPES) or is_module(v))
                }
                # print(filtered_locals)
                for key in filtered_locals:
                    logger.debug(f"Local variable: {key}")
                self._locals_before = copy.deepcopy(filtered_locals)

            return self if self.manual else None
        except Exception as e:
            logger.error(f"[QSPy][ERROR] Exception on entering context: {e}")
            raise

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Exit the context manager.

        Detects new variables, validates, and adds components to the model.
        In manual mode, adds components explicitly provided via __call__.

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

        logger = logging.getLogger(LOGGER_NAME)
        try:
            logger.info(f"[QSPy] Exiting context: {self.__class__.__name__}")
            if self.manual:
                for name, *args in self._manual_adds:
                    self._add_component(name, *args)
            else:
                # Filter out model components and context objects before comparison

                filtered_locals = {
                    k: v
                    for k, v in self._frame.f_locals.items()
                    if not ((hasattr(v, "__class__") and k in SKIP_TYPES) or is_module(v))
                }
                new_vars = set(filtered_locals.keys()) - set(self._locals_before.keys())

                for var_name in new_vars:
                    val = filtered_locals[var_name]
                    args = self._validate_value(var_name, val)
                    # Remove the name from the frame locals so it
                    # can be re-added as the component.
                    del self._frame.f_locals[var_name]
                    self._add_component(var_name, *args)
            # for component in self.components:
            #     if component.name in set(self._frame.f_locals.keys()):
            #         self._frame.f_locals[component.name] = component
        except Exception as e:
            logger.error(f"[QSPy][ERROR] Exception on exiting context: {e}")

    def __call__(self, name, *args):
        """
        Add a component manually (manual mode only).

        Parameters
        ----------
        name : str
            Name of the component.
        *args
            Arguments for component creation.

        Raises
        ------
        RuntimeError
            If called when manual mode is not enabled.
        """
        if not self.manual:
            raise RuntimeError(
                f"Manual mode is not enabled for this {self.__class__.__name__}"
            )
        self._manual_adds.append((name, *args))

    def _add_component(self, name, *args):
        """
        Validate and add a component to the model.

        Parameters
        ----------
        name : str
            Name of the component.
        *args
            Arguments for component creation.

        Raises
        ------
        ValueError
            If the component already exists in the model.
        """
        if name in self.model.component_names:
            raise ValueError(
                f"{self.component_name.capitalize()} '{name}' already exists in the model."
            )

        component = self.create_component(name, *args)
        self.add_component(component)

        if self.verbose:
            print(f"[{self.component_name}] Added: {name} with args: {args}")

    def _validate_value(self, name, val):
        """
        Validate or transform the right-hand-side value.

        Override in subclasses if custom validation or transformation is needed.

        Parameters
        ----------
        name : str
            Name of the variable.
        val : object
            Value assigned to the variable.

        Returns
        -------
        tuple
            Arguments to be passed to create_component.

        Raises
        ------
        ValueError
            If the value is not a tuple.
        """
        if not isinstance(val, tuple):
            raise ValueError(
                f"{self.component_name.capitalize()} '{name}' must be defined as a tuple."
            )
        return val

    @abstractmethod
    def create_component(self, name, *args):
        """
        Abstract method to create a component.

        Must be implemented in subclasses.

        Parameters
        ----------
        name : str
            Name of the component.
        *args
            Arguments for component creation.

        Raises
        ------
        NotImplementedError
            Always, unless implemented in subclass.
        """
        raise NotImplementedError

    def add_component(self, component):
        """
        Add the component to the model.

        Parameters
        ----------
        component : pysb.Component
            The component to add.
        """
        # self.components.add(component)
        self.model.add_component(component)
