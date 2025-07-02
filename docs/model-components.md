# Model Components

## From PySB to QSPy: Building with Context

At its core, QSPy builds on [PySB](https://pysb.org/), a Python-embedded domain specific language (DSL) for rule-based modeling. PySB defines models through components such as **Monomers**, **Parameters**, **Rules**, **Initials**, and **Observables**, which together specify the structure and dynamics of a biological system.

QSPy preserves this foundational API while introducing a structured, context-based approach to model definition.

Instead of just writing all components imperatively at the module level, QSPy allows grouping them into **named contexts** using Python `with` blocks:

```python
with monomers():
    Ligand = (["r"], None, PROTEIN.LIGAND)
    Receptor = (["l"], None, PROTEIN.RECEPTOR)
```

This organizational style mimics classic declarative DSLs like BioNetGen and rxode2, promoting:

  - Leaner model encoding, especially when definining large numbers of components
  - Enhanced readability
  - Semantic grouping of components

The sections that follow describe each model component and how QSPy extends their definition.

## The Model Object

Every QSPy model builds upon a central `Model` object that serves as the container for all biological components, relationships, and metadata. This object is an extension of the standard PySB `Model` object, with additional hooks for logging, metadata tracking, and QSPy’s context-aware construction pattern, as well as additional utilities for setting global model units and outputting model summaries to [Markdown](https://en.wikipedia.org/wiki/Markdown) files.

As with PySB, a new `Model` is typically specified in Python module file (e.g., `model.py`). When you define a `Model` in QSPy, a global `model` object is automatically available like in PySB. All subsequent context blocks, such as `with monomers()` or with `parameters()`, register their components to this object. Also, as in PySB, any model components created using their class-based objects, such as `Parameter(...)` or `Rule(...)`, are also automatically registered to the model object.

```python
Model().with_units(concentration="mg/L", time="h", volume="L")
```

As above, we recommend always chaining `Model` initialization with the `with_units` function to set global model units for concentration, time, and volume; all subsequent parameter definitions with these unit types will be automatically converted and appropriately scaled behind the scenes during model import.

After model specification (e.g., in `my_model.py`), the `model` object can imported and used accordingly.

```python
from my_model import model
```

## Monomers

`Monomer`s represent fundamental molecular and biological species, such as drugs, proteins, or receptors. They have _sites_ and _site states_, and can also be assigned a [functional tag](./functional-tags.md). _Sites_ may represent binding regions or other modifiable molecular features, such as phosphorylation sites with distinct states (e.g., unphosphorylated `'u'` and phosphorylated `'p'`). 

With `monomers` context:
```python
with monomers():
    Ligand = (["r"], None, DRUG.INHIBITOR)
    Receptor = (["l"], None, PROTEIN.RECEPTOR)
```
Inside the `monomers` context the assignment pattern is:

    monomer_name = (sites_list, site_states_dict, functional_tag)


Context-free equivalent:
```python
Monomer("Ligand", ['r']) @ DRUG.INHIBITOR
Monomer("Receptor", ['l']) @ PROTEIN.RECEPTOR
```

Assigning a functional tag inside the `monomers` context is optional, so the following pattern is also valid:
with monomers():
    Ligand = (["r"], None)
    Receptor = (["l"], None)
```

**QSPy enhancements:**

- Functional tagging (e.g., PROTEIN.RECEPTOR, DRUG.INHIBITOR), including new `@` operator for functional tag assignments.
- Contextual grouping with automatic introspection for monomer creation and naming (when using `monomers` context).

## Parameters

`Parameter`s quantify rate constants, concentrations, or other numeric values.

With `parameters` context:
```python
with parameters():
    kf_bind = (1e-1, "1/uM/s")
    kr_bind = (1e-3, "1/s")
    Ligand_0 = (100, "nM")
```
Inside the `parameters` context the assignment pattern is:

    parameter_name = (value, units)

Context-free equivalent:
```python
Parameter("kf_bind", 1e-1, unit="1/uM/s")
Parameter("kr_bind", 1e-3, unit="1/s")
Parameter("Ligand_0" 100, unit="nM")
```

**QSPy enhancements:**

- Native support for units (e.g., mg, nM, hr⁻¹, L/min)
- Contextual grouping with automatic introspection for parameter creation and naming (when using `parameters` context).

## Rules

`Rules` define biochemical interactions such as binding or transformation.

With `rules` context:
```python
with rules():
    bind_L_R = (Ligand(r=None) + Receptor(l=None) >> Ligand(r=1) % Receptor(l=1), kf_bind, kr_bind)
```
Inside the `rules` context the assignment pattern is:

reversible:

    rule_name = (reaction pattern, forward rate consant, reverse rate constant)


irreversible:

    rule_name = (reaction pattern, rate constant)


Context-free equivalent:
```python
Rule("bind_L_R", Ligand(r=None) + Receptor(l=None) >> Ligand(r=1) % Receptor(l=1), kf_bind, kr_bind)
```

**QSPy enhancements:**

- Contextual grouping with automatic introspection for rule creation and naming (when using `rules` context).

## Initial Conditions

`Initial`s specify the starting concentrations or states of species in the model.

With `initials` context:
```python
with initials():
    Ligand(r=None) << Ligand_0
```
Context-free equivalent:
```python
Ligand(r=None) << Ligand_0
```
Without the `<<` operator:
```python
Initial(Ligand(r=None), Ligand_0)
```

**QSPy enhancements:**

- Optional grouped `initials` context for clearer organization
- New `<<` operator for initial condition assignment without the need to explicitly initialize an `Initial` object.

## Observables

`Observable`s define measurable quantities derived from model states.

With `observables` context:
```python
with observables():
    Ligand(r=1) % Receptor(l=1) > "BoundComplex"
```
OR with automatic name assignment using the `~` prefix operator:
```python
with observables():
    ~Ligand(r=1) % Receptor(l=1)
```
Context-free equivalent with `<` operator:
```python
Ligand(r=1) % Receptor(l=1) > "BoundComplex"
```
Context-free equivalent with `~` operator:
```python
~Ligand(r=1) % Receptor(l=1)
```
Context-free and Without the `>` or `~` operators:
```python
Observable("BoundComplex", Ligand(r=1) % Receptor(l=1))
```

**QSPy enhancements:**

- Optional grouped `observables` context for clearer organization
- New `>` operator for observable assignment without the need to explicitly initialize an `Observable` object.
- New `~` operator for observable assignment with an auto-generated name, and without the need to explicitly initialize an `Observable` object.

## Expressions

Expressions define algebraic relationships between parameters, observables, or other expressions. They’re useful for computing composite values like dose scaling factors, compartment-adjusted concentrations, or feedback-modulated rates.

With `expressions` context:

```python
with expressions():
    K_d = k_r / k_f # dissociation constant
```
Context-free equivalent:
```python
Expression("K_d", k_r / k_f) # dissociation constant
```

**QSPy enhancements:**

- Contextual grouping with automatic introspection for expression creation and naming (when using `expressions` context).

## Compartments

`Compartment`s define spatial contexts for species and reactions, representing physical volumes or surfaces such as plasma, tissue, or organelles.

```python
with parameters():
    V_C = (10.0, "L")
    V_P = (100.0, "mL")

with compartments():
    CENTRAL = V_C
    PERIPHERAL = V_P
``` 
Context-free equivalent:
```python
Parameter("V_C", 10.0, unit="L")
Parameter("V_P", 100.0, unit="mL")

Compartment("CENTRAL", size=V_C)
Compartment("PERIPHERAL", size=V_P)
```

**QSPy enhancements:**

- Contextual grouping with automatic introspection for compartment creation and naming (when using `compartments` context).