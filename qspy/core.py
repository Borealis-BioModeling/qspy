import pysb.units
from pysb.units.core import *
from pysb.core import SelfExporter

__all__ = pysb.units.core.__all__

class Model(Model):
    # def __init__(
    #     self,
    #     name=None,
    #     base=None,
    #     units={"concentration": "mg/L", "time": "h", "volume": "L"},
    # ):
    #     super().__init__(name='model', base=base)
    #     #SelfExporter.export(self)
    #     SimulationUnits(**units)
    #     return
    
    @staticmethod
    def with_units(concentration: str = "mg/L", time: str = "h", volume: str = 'L'):
        SimulationUnits(concentration, time, volume)
        return

    
    @property
    def component_names(self):
        return [component.name for component in self.components]
