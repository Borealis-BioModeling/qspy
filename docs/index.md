---
icon: material/home
---

# Welcome to `QSPy`'s Documentation

_**QSPy**: Quantitative Systems Pharmacology in Python_

## Overview

`QSPy` (pronounced _"Cue Ess Pie"_) is a [Python](https://www.python.org/) framework for building modular, rule-based models that describe drug behavior and pharmacological interactions within biological systems. Leveraging the power of [PySB](https://pysb.org/), it streamlines the development, simulation, and analysis of **quantitative systems pharmacology (QSP)** models through a reproducible and programmatic approach.


### Key Features

- **Contextualized model definition** - QSPy introduces a block-based extension of the PySB domain-specific language (DSL) that organizes model components (monomers, parameters, rules, etc.) into named contexts, more closely mimicking the feel of traditional, block-based, DSLs like [BioNetGen](https://bionetgen.org/), [rxode2](https://nlmixr2.github.io/rxode2/), and [mrgsolve](https://mrgsolve.org/). This structure streamlines model definition and improves readability, while remaining fully interoperable with standard class-based definitions and preserving the full flexibility of PySB’s Python-embedded framework.

| PySB  components | QSPy contexts |
| ---- | ------------- |
| <script src="https://gist.github.com/blakeaw/4c57d06538570701811c3556d72741ae.js"></script> | <script src="https://gist.github.com/blakeaw/255e5a3a6358985b452f336f51107304.js"></script> |

- **Native support for units** - In QSPy, models and their parameters can be assigned physical units (e.g., `mg`, `nM`, `hr⁻¹`, `L/min`), enabling automatic conversions, dimensional analysis, and consistency checking.

- **Initial model validation tools** - QSPy provides a `ModelChecker` utility that automatically identifies unused components, zero-valued parameters, missing initial conditions, and overdefined reactions. Warnings are surfaced in real time during model import, with structured logs exported for reproducibility and review.

- **Metadata tracking** - QSPy includes a `ModelMetadataTracker` object that attaches key information, such as author, model version, Python environment, and package versions, directly to the model. This metadata can be exported to a `.toml` file that's both human- and machine-readable, making it easy to track provenance and support downstream reporting or validation workflows.

- **Built-in logging** - Model construction steps, metadata, and redacted provenance are logged to `.qspy/` folders, giving you a reproducible and inspectable trail for every model version.

- **Functional monomer tagging** - QSPy introduces structured tags for classifying monomer components by biological role or modeling intent: e.g., `PROTEIN.RECEPTOR` and `DRUG.INHIBITOR`. These tags add additional expressiveness to model species and enable an additional way to filter monomer components for searches and analyses.
```python
# Using @ operator
Monomer('Drug', ['b']) @ DRUG.INHIBITOR

# Using @= operator
Monomer('Target', ['b'])
Target @= PROTEIN.RECEPTOR

# Inside monomers context
with monomers():
    Decoy = (['b'], None, PROTEIN.RECEPTOR)
```


### Why `QSPy`?

- **Programmatic Modeling** – Enables automated workflows, reproducibility (_e.g., version control and automated testing_), customization, and creation of reusable functions for pharmacological and biochemical processes.
- **Built-in Support for Mechanistic Modeling** – QSPy is built on [PySB](https://pysb.org/)'s mechanistic modeling framework, allowing you to incorporate biochemical mechanisms and build customized mechanistic PK/PD and QSP/QST models.
- **Rule-Based Approach** – Encode complex pharmacological and biochemical processes using intuitive [rule-based modeling](https://en.wikipedia.org/wiki/Rule-based_modeling). No need to enumerate all reactions/molecular species or manually encode the corresponding network of differential equations.
- **Python-Based** – Seamlessly integrates with Python’s scientific computing ecosystem, supporting advanced simulations, data analysis, and visualization.
- **Arbitrary Number of Compartments** – Specify any number of compartments to build custom multi-compartment models, including complex drug distribution and physiologically-based pharmacokinetic (PBPK) models.
- **Enhanced reproducibility and reporting** - With built in tools like the `ModelChecker` and `ModelMetadataTracker`, you can automatically catch potential issues with model structure or components early while also tracking relevant metadata for downstream reproduction and reporting.   
- **Open-Source** - QSPy is free and open-source, meaning it is freely available and fully customizable.

------

## Dependencies

`QSPy` has the following core dependencies:

  * [PySB](https://pysb.org/)
  * [pysb-pkpd](https://blakeaw.github.io/pysb-pkpd/)
  * [pysb-units](https://github.com/Borealis-BioModeling/pysb-units)
  * [pysb-fit](https://github.com/Borealis-BioModeling/pysb-fit)
  * [microbench](https://github.com/alubbock/microbench)

## Installation
  1. Install **PySB** using [conda](https://docs.conda.io/en/latest/) or [mamba](https://github.com/mamba-org/mamba):
    ```sh
    conda install -c alubbock pysb
    ```
    **OR**
    ```sh
    mamba install -c alubbock pysb
    ```    
  2. Install **pysb-pkpd** with pip:
    ```sh
    pip install pysb-pkpd
    ```
Ensure you have Python 3.11.3+ and PySB 1.15.0+ installed.

## Quick-start Example

```python
from qspy import Model, parameters, monomers, rules, initials, observables
from qspy.functionaltags import PROTEIN, DRUG
from qspy.validation import ModelMetadataTracker, ModelChecker

Model(name="SimpleQSP").with_units(concentration='nM', time='1/s', volume='L')

with parameters():
    k_f = (1.0, "1/min")
    k_r = (0.5, "1/min")
    L_0 = (100.0, "nM")
    R_0 = (10.0, "nM")

with monomers():
    L = (["b"], {}, DRUG.AGONIST)
    R = (["b", 'active'], {'active':[False, True]}, PROTEIN.RECEPTOR)

with rules():
    bind = (L(b=None) + R(b=None, active=False) | L(b=1) % R(b=1, active=True), k_f, k_r)

with initials():
    L(b=None) << L_0
    R(b=None, active=False) << R_0

with observables():
    L() > "L_total"
    R() > "R_total"
    R(active=True) > "R_active"

# Track and export model metadata
ModelMetadataTracker(version="1.0.0", author="Alice", export_toml=True)

# Run model validation checks
Model

# Generate a Markdown summary
model.summarize()
               
```


## Acknowledegments

Special thanks for [Martin Breuss's MkDocs tuorial](https://realpython.com/python-project-documentation-with-mkdocs/#step-2-create-the-sample-python-package), which served as the template for setting up and generating documentation using Mkdocs.

**AI Acknowledgement**

Generative AI tools, including ChatGPT, Microsoft Copilot, and GitHub Copilot, were used to brainstorm features and implementation details, draft initial code snippets and boilerplate, and support documentation through outlining, editing, and docstring generation.