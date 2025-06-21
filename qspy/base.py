import inspect
import copy
import weakref
from abc import ABC, abstractmethod
from pysb.core import SelfExporter, ComponentSet


class ComponentContext(ABC):
    component_name = "component"  # e.g. 'parameter', 'monomer'

    def __init__(self, manual: bool = False, verbose: bool = False):
        self.manual = manual
        self.verbose = verbose
        self._manual_adds = []
        self._frame = None
        self._locals_before = None
        # self.components = ComponentSet()
        self.model = SelfExporter.default_model
        self._override = False

    def __enter__(self):
        
        if self.model is None:
            raise RuntimeError("No active model found. Did you instantiate a Model()?")
        if self._override:
            self._frame = inspect.currentframe().f_back.f_back
        else:
            self._frame = inspect.currentframe().f_back

        # Require module-level use for introspection mode
        if ((not self.manual) and (self._frame.f_globals is not self._frame.f_locals)) and (not self._override):
            raise RuntimeError(
                f"{self.__class__.__name__} must be used at module scope. "
                f"Wrap model components in a module-level script."
            )

        if not self.manual:
            for key in self._frame.f_locals:
                print(key)
            self._locals_before = copy.deepcopy(self._frame.f_locals)

        return self if self.manual else None

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.manual:
            for name, *args in self._manual_adds:
                self._add_component(name, *args)
        else:
            new_vars = set(self._frame.f_locals.keys()) - set(
                self._locals_before.keys()
            )

            for var_name in new_vars:
                val = self._frame.f_locals[var_name]
                args = self._validate_value(var_name, val)
                # Remove the name from the frame locals so it
                # can be re-added as the component.
                del self._frame.f_locals[var_name]
                self._add_component(var_name, *args)
        # for component in self.components:
        #     if component.name in set(self._frame.f_locals.keys()):
        #         self._frame.f_locals[component.name] = component
        return

    def __call__(self, name, *args):
        if not self.manual:
            raise RuntimeError(
                f"Manual mode is not enabled for this {self.__class__.__name__}"
            )
        self._manual_adds.append((name, *args))

    def _add_component(self, name, *args):
        if name in self.model.component_names:
            raise ValueError(
                f"{self.component_name.capitalize()} '{name}' already exists in the model."
            )

        component = self.create_component(name, *args)
        self.add_component(component)

        if self.verbose:
            print(f"[{self.component_name}] Added: {name} with args: {args}")

    def _validate_value(self, name, val):
        """Override if the subclass needs to transform the RHS value"""
        if not isinstance(val, tuple):
            raise ValueError(
                f"{self.component_name.capitalize()} '{name}' must be defined as a tuple."
            )
        return val

    @abstractmethod
    def create_component(self, name, *args):
        raise NotImplementedError

    def add_component(self, component):
        # self.components.add(component)
        self.model.add_component(component)
