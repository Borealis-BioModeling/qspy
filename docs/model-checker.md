# `ModelChecker`: Validating Model Integrity in QSPy

The `ModelChecker` is QSPy's built-in utility for diagnosing and validating model integrity before simulation. It inspects models to identify potential errors, such as unused components, zero-valued parameters, missing initial conditions and lack consistency amongst physical units. Errors and warnings are surfaced in real time during model import, with structured logs exported for reproducibility and review.

---

## Key Features

Includes checks for:

- _Unused components_: Warns of any unused monomers or parameters.
- _Zero-valued parameters_: Warns of any parameters with a value of zero.
- _Dangling or Re-used bonds_: Raises errors for any dangling or re-used bonds in reaction rules.
- _Units Checks_: Warns of any duplicate, inconsistent, or missing units.

---

## Importing and Instantiating

Inside model definition:

```python
from qspy.validation import ModelChecker
...
Model().with_units(...)
...
...
# Runs validation checks when model is imported.
ModelChecker()
```

Outside of model definition:

```python
from qspy.validation import ModelChecker
from my_model import model  # build programmatically

checker = ModelChecker(model)
```
