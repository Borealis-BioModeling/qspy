# Building a Model with QSPy

This guide walks through encoding a model directly in Python using QSPy’s core modules. For this purpose, we will build a relatively simple two-compartment semi-mechanistic pharmacokinetics & receptor-occupancy (PKRO) model. Typically, models are defined in their own Python module file: e.g., `pkro_model.py`.

## 1) Import essential modules/objects

```python
from qspy import *
```

## 2) Create and instance of the Model class and specify global model units.

```python
Model().with_units(concentration="mg/L", time="h", volume="L")
```

## 3) Specify model parameters

```python
with parameters():
    # drug dose
    drug_dose = (100.0, "mg")
    # Compartment volumes
    V_CENTRAL = (10.0, "L")
    V_PERIPHERAL = (1.0, "L")
    # drug distribution rate constants
    k_CP = (1e-1, "1/s")
    k_PC = (1e-3, "1/s")
    # receptor density
    receptor_0 = (100.0, "ug/L")
    # receptor binding rate constants
    k_f = (1.0, "L/(ug * s)")
    k_r = (1e-3, "1/s")
```

## 4) Define any expressions

```python
with expressions():
    # Initial drug concentration - bolus dose
    drug_0 = drug_dose / V_CENTRAL
```

## 5) Specify the model compartments

```python
with compartments():
    CENTRAL = V_CENTRAL
    PERIPHERAL = V_PERIPHERAL
```

## 6) Define any monomer species

```python
with monomers():
    drug = (['b'], None, DRUG.AGONIST)
    receptor = (['b'], None, PROTEIN.RECEPTOR)
```

## 7) Specify initial conditions

```python
with initials():
    drug(b=None)**CENTRAL << drug_0
    receptor(b=None)**PERIPHERAL << receptor_0
```

## 8) Define reaction rules

```python
with rules():
    # Distribution
    drug_distribution = (drug(b=None)**CENTRAL | drug(b=None)**PERIPHERAL, k_CP, k_PC)
    # Receptor binding
    receptor_binding = (drug(b=None)**PERIPHERAL + receptor(b=None)**PERIPHERAL | drug(b=1)**PERIPHERAL % receptor(b=1)**PERIPHERAL, k_f, k_r)
```

## 9) Assign observables

```python
with observables():
    drug(b=1)**PERIPHERAL % receptor(b=1)**PERIPHERAL > "OccupiedReceptor"
```

## 10) Assign model metadata and tracker (optional)

```python
__version__ = 0.1.0
__author__ = "Jane Doe"
ModelMetadataTracker(__version__, author=__author__)
```

!!! info
    Learn more about the [metadata tracker](./metadata-tracking.md)

## 11) Initialize model checker (optional)

```python
ModelChecker()
```

!!! info
    Learn more about the [model checker](./model-checker.md)

## 12) Include a mermaid diagram generator (optional)

```python
ModelMermaidDiagrammer()
```

!!! info
    Learn more about the [diagram generator](./model-diagram-generator.md)

------

## Full example model

!!! example "pkro_model.py"

    ```python
    from qspy import *

    with parameters():
        # drug dose
        drug_dose = (100.0, "mg")
        # Compartment volumes
        V_CENTRAL = (10.0, "L")
        V_PERIPHERAL = (1.0, "L")
        # drug distribution rate constants
        k_CP = (1e-1, "1/s")
        k_PC = (1e-3, "1/s")
        # receptor density
        receptor_0 = (100.0, "ug/L")
        # receptor binding rate constants
        k_f = (1.0, "L/(ug * s)")
        k_r = (1e-3, "1/s")

    with expressions():
        # Initial drug concentration - bolus dose
        drug_0 = drug_dose / V_CENTRAL

    with compartments():
        CENTRAL = V_CENTRAL
        PERIPHERAL = V_PERIPHERAL

    with monomers():
        drug = (['b'], None, DRUG.AGONIST)
        receptor = (['b'], None, PROTEIN.RECEPTOR)

    with initials():
        drug(b=None)**CENTRAL << drug_0
        receptor(b=None)**PERIPHERAL << receptor_0

    with rules():
        # Distribution
        drug_distribution = (drug(b=None)**CENTRAL | drug(b=None)**PERIPHERAL, k_CP, k_PC)
        # Receptor binding
        receptor_binding = (drug(b=None)**PERIPHERAL + receptor(b=None)**PERIPHERAL | drug(b=1)**PERIPHERAL % receptor(b=1)**PERIPHERAL, k_f, k_r)

    with observables():
        drug(b=1)**PERIPHERAL % receptor(b=1)**PERIPHERAL > "OccupiedReceptor"

    __version__ = 0.1.0
    __author__ = "Jane Doe"
    ModelMetadataTracker(__version__, author=__author__)
    ModelMermaidDiagrammer()
    ModelChecker()
    ```