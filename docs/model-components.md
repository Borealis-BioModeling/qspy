# Model Components

## From PySB to QSPy: Building with Context

At its core, QSPy builds on [PySB (Python Systems Biology modeling)](https://pysb.org/), a Python-embedded domain specific language (DSL) for rule-based modeling of biochemical systems. PySB models are constructed from core components such as **Monomers**, **Parameters**, **Rules**, **Initials**, and **Observables**. It adopts an object-oriented approach to model building, enhanced with syntactic sugar for automatic component registration (self-exporting) and a chemistry-inspired rule syntax based on [BNGL (BioNetGen Language)](https://bionetgen.org/). QSPy preserves this foundational API while introducing an alternative, structured, context-based approach to model definition. 

Instead of directly initializing instances of component classes, QSPy allows grouping them into **named contexts** using Python `with` blocks.

!!! example
    ```python
    with monomers():
        Ligand = (["r"], None, PROTEIN.LIGAND)
        Receptor = (["l"], None, PROTEIN.RECEPTOR)
    ```

Where applicable, QSPy then parses the inputs into the desired model components during the context exit process. As in PySB, the component names are exported into the current namespace, and the components can be programmatically manipulated.

!!! example
    ```python
    print(Ligand)
    ```
    
        >>> Monomer("Ligand", ['r']) @ protein::ligand

This organizational style mimics the block-based structure of classic declarative DSLs, such as [BNGL](https://bionetgen.org/) and [rxode2](https://nlmixr2.github.io/rxode2/) model specificaitons, while preserving the flexibility of a programmatic Python environment. The goal is to further streamline model encoding and improve readability by minimizing boilerplate and promoting semantic grouping of related model components. 

!!! note
    QSPy contexts also incorporate logging functionality to help users track component additions and audit model assembly for reproducibility.

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

=== "With `monomers` context:"
    ```python
    with monomers():
        Ligand = (["r"], None, DRUG.INHIBITOR)
        Receptor = (["l"], None, PROTEIN.RECEPTOR)
    ```

=== "Context-free equivalent"
    ```python
    Monomer("Ligand", ['r']) @ DRUG.INHIBITOR
    Monomer("Receptor", ['l']) @ PROTEIN.RECEPTOR
    ```

!!! note 

    Inside the `monomers` context the assignment pattern is:

        monomer_name = (sites_list, site_states_dict, functional_tag)

    Also, assigning a functional tag inside the `monomers` context is optional, so the following pattern is also valid:

    ```python
    with monomers():
        Ligand = (["r"], None)
        Receptor = (["l"], None)
    ```

!!! info "QSPy enhancements"
    - Functional tagging (e.g., `PROTEIN.RECEPTOR`, `DRUG.INHIBITOR`), including new overloaded `@` operator for functional tag assignments.
    - Contextual grouping with automatic introspection for monomer creation and naming (when using `monomers` context).

## Parameters

`Parameter`s quantify rate constants, concentrations, or other numeric values.

=== "With `parameters` context:"
    ```python
    with parameters():
        kf_bind = (1e-1, "1/uM/s")
        kr_bind = (1e-3, "1/s")
        Ligand_0 = (100, "nM")
    ```
=== "Context-free equivalent:"
    ```python
    Parameter("kf_bind", 1e-1, unit="1/uM/s")
    Parameter("kr_bind", 1e-3, unit="1/s")
    Parameter("Ligand_0" 100, unit="nM")
    ```

!!! note 
    inside the `parameters` context the assignment pattern is:

        parameter_name = (value, units)

!!! info "QSPy enhancements"
    - Native support for units (e.g., mg, nM, hr⁻¹, L/min)
    - Contextual grouping with automatic introspection for parameter creation and naming (when using `parameters` context).

## Rules

`Rules` define biochemical interactions such as binding or transformation.

=== "With `rules` context:"
    ```python
    with rules():
        bind_L_R = (Ligand(r=None) + Receptor(l=None) 
        >> Ligand(r=1) % Receptor(l=1), kf_bind, kr_bind
        )
    ```

=== "Context-free equivalent:"
    ```python
    Rule("bind_L_R", Ligand(r=None) + Receptor(l=None) \
    >> Ligand(r=1) % Receptor(l=1), kf_bind, kr_bind)
    ```

!!! note 
    inside the `rules` context the assignment pattern is:

    :left_right_arrow: reversible reactions:

        rule_name = (reaction pattern, forward rate consant, reverse rate constant)


    :arrow_right: irreversible reactions:

        rule_name = (reaction pattern, rate constant)

!!! info "QSPy enhancements"
    - Contextual grouping with automatic introspection for rule creation and naming (when using `rules` context).

## Initial Conditions

`Initial`s specify the starting concentrations or states of species in the model.

=== "With `initials` context:"
    ```python
    with initials():
        Ligand(r=None) << Ligand_0
    ```

=== "Context-free equivalent:"
    ```python
    Ligand(r=None) << Ligand_0
    ```
=== "Context-free without the `<<` operator:"
    ```python
    Initial(Ligand(r=None), Ligand_0)
    ```

!!! info "QSPy enhancements"
    - Optional grouped `initials` context for clearer organization and additional logging
    - New overloaded `<<` operator for initial condition assignment without the need to explicitly initialize an `Initial` object.

## Observables

`Observable`s define measurable quantities derived from model states.

=== "With `observables` context:"
    ```python
    with observables():
        Ligand(r=1) % Receptor(l=1) > "BoundComplex"
    ```
=== "auto naming using `~` prefix operator:"
    ```python
    with observables():
        ~Ligand(r=1) % Receptor(l=1)
    ```
=== "Context-free equivalent with `>` operator:"
    ```python
    Ligand(r=1) % Receptor(l=1) > "BoundComplex"
    ```
=== "Context-free equivalent with `~` operator:"
    ```python
    ~Ligand(r=1) % Receptor(l=1)
    ```
=== "Context-free without the `>` or `~` operators:"
    ```python
    Observable("BoundComplex", Ligand(r=1) % Receptor(l=1))
    ```

!!! info "QSPy enhancements"
    - Optional grouped `observables` context for clearer organization and additional logging
    - New overloaded `>` operator for observable assignment without the need to explicitly initialize an `Observable` object.
    - New overloaded `~` operator for observable assignment with an auto-generated name, and without the need to explicitly initialize an `Observable` object.

## Expressions

Expressions define algebraic relationships between parameters, observables, or other expressions. They’re useful for computing composite values like dose scaling factors, compartment-adjusted concentrations, or feedback-modulated rates.

=== "With `expressions` context:"
    ```python
    with expressions():
        K_d = k_r / k_f # dissociation constant
    ```
=== "Context-free equivalent:"
    ```python
    Expression("K_d", k_r / k_f) # dissociation constant
    ```

!!! info "QSPy enhancements"
    - Contextual grouping with automatic introspection for expression creation and naming (when using `expressions` context).

## Compartments

`Compartment`s define spatial contexts for species and reactions, representing physical volumes or surfaces such as plasma, tissue, or organelles.

=== "With contexts"
    ```python
    with parameters():
        V_C = (10.0, "L")
        V_P = (100.0, "mL")

    with compartments():
        CENTRAL = V_C
        PERIPHERAL = V_P
    ``` 
=== "Context-free equivalent:"
    ```python
    Parameter("V_C", 10.0, unit="L")
    Parameter("V_P", 100.0, unit="mL")

    Compartment("CENTRAL", size=V_C)
    Compartment("PERIPHERAL", size=V_P)
    ```

!!! info "QSPy enhancements"
    - Contextual grouping with automatic introspection for compartment creation and naming (when using `compartments` context).

## Macros

Macros in QSPy provide high-level, reusable templates for common biochemical processes such as binding, catalysis, synthesis, degradation, and more. They encapsulate complex rule patterns into a single, expressive statement, improving both readability and maintainability of your model code.

### Background: PySB Macros

[PySB macros](https://pysb.readthedocs.io/en/stable/tutorial.html#using-provided-macros) are functions that generate sets of rules and components for common biochemical motifs (e.g., reversible binding, catalysis, synthesis, degradation). They are a foundational feature of PySB, enabling concise and readable model code for complex biological processes.

QSPy builds on this foundation by:

- **Incorporating all core PySB macros** (`pysb.macros`) as `qspy.macros.core` (these include functions like `bind`, `equilibrate`, `catalyze`, etc.)
- **Including the PK/PD macros** from [`pysb-pkpd`](https://blakeaw.github.io/pysb-pkpd/macros/) (`pysb.pkpd.macros`) as `qspy.macros.pkpd` (these include PK processes such as `distribute` and `eliminate`, PD functions like `emax`, and `sigmoidal_emax`, and dosing functions like `dose_bolus`)
- **Adding native support for units** to both sets of macros, so all rate and concentration parameters can be specified with units and are automatically converted and checked

This means you can use all standard PySB macro patterns in QSPy, but with enhanced unit handling and integration with QSPy’s context and logging system.

### QSPy Macro Contexts

You can use macros directly or within the `macros` context for grouped, introspective macro registration. When using the `macros` context, all macro-generated components are automatically logged to the QSPy logs for auditability and reproducibility.

=== "With `macros` context:"
    ```python
    with macros():
        bind(Ligand(r=None), Receptor(l=None), 'r', 'l', [kf_bind, kr_bind])
        degrade(Protein(), k_deg)
    ```
=== "Context-free equivalent:"
    ```python
    bind(Ligand(r=None), Receptor(l=None), 'r', 'l', [kf_bind, kr_bind])
    degrade(Protein(), k_deg)
    ```

!!! info "QSPy enhancements"
    - All macros are updated to use unit-aware model components.
    - Contextual grouping with automatic introspection and logging when using the `macros` context.
    - Full access to both core PySB macros and PK/PD macros from `pysb-pkpd`.

Macros can greatly simplify the specification of complex reaction patterns, especially when used in combination with QSPy’s context system.

For more details on available macros, see the [PySB macro documentation](https://pysb.readthedocs.io/en/stable/tutorial.html#using-provided-macros) and the [pysb-pkpd macro documentation](https://blakeaw.github.io/pysb-pkpd/macros/).