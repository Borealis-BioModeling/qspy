from pathlib import Path
from datetime import datetime
import os
from pysb.export import export as pysb_export

try:
    import SBMLDiagrams
    HAS_SBMLDIAGRAMS = True
except ImportError:
    HAS_SBMLDIAGRAMS = False
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
    


    def summarize(self, path=".qspy/model_summary.md", include_diagram=True):
        """Generate a Markdown summary of the model and optionally a diagram."""
        lines = []
        lines.append(f"# QSPy Model Summary: `{self.name}`\n")

        metadata = getattr(self, "qspy_metadata", {})
        lines.append(f"**Model name**: `{self.name}`")
        lines.append(f"**Hash**: `{metadata.get('hash', 'N/A')}`")
        lines.append(f"**Version**: {metadata.get('version', 'N/A')}")
        lines.append(f"**Author**: {metadata.get('author', 'N/A')}")
        lines.append(f"**Executed by**: {metadata.get('current_user', 'N/A')}")
        lines.append(f"**Timestamp**: {metadata.get('created_at', datetime.now().isoformat())}\n")

        if include_diagram and HAS_SBMLDIAGRAMS:
            diagram_path = Path(".qspy/model_diagram.png")
            diagram_path.parent.mkdir(parents=True, exist_ok=True)
            sbml_str = pysb_export(self, 'sbml')
            with open(".qspy/temp_model.xml", "w") as f:
                f.write(sbml_str)
            diagram = SBMLDiagrams.load(".qspy/temp_model.xml")
            diagram.draw(output_file=str(diagram_path))
            lines.append("## 🖼️ Model Diagram\n")
            lines.append(f"![Model Diagram]({diagram_path})\n")

        lines.append("## Monomers")
        lines += [f"- `{m.name}` with sites `{m.sites}` and states `{m.site_states}`" for m in self.monomers] or ["_None defined_"]

        lines.append("\n## Parameters\n| Name | Value | Units |")
        lines.append("|------|--------|--------|")
        lines += [f"| {p.name} | {p.value} | {p.unit.to_string()} |" for p in self.parameters] or ["| _None_ | _N/A_ |"]

        lines.append("\n## Initial Conditions\n| Species | Value | Units |")
        lines.append("|---------|--------|--------|")
        lines += [f"| {str(ic[0])} | {ic[1].value if isinstance(ic[1], Parameter) else ic[1].get_value()} | {ic[1].units.value}" for ic in self.initial_conditions] or ["| _None_ | _N/A_ |"]

        lines.append("\n## Rules")
        lines += [f"- `{repr(r)}`" for r in self.rules] or ["_None defined_"]

        lines.append("\n## Observables")
        lines += [f"- `{o.name}`" for o in self.observables] or ["_None defined_"]

        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))


