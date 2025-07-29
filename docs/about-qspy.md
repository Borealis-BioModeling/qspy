# About QSPy

## Why `QSPy`?

- **Programmatic Modeling** – Enables automated workflows, reproducibility (_e.g., version control and automated testing_), customization, and creation of reusable functions for pharmacological and biochemical processes.
- **Built-in Support for Mechanistic Modeling** – QSPy is built on [PySB](https://pysb.org/)'s mechanistic modeling framework, allowing you to incorporate biochemical mechanisms and build customized mechanistic PK/PD and QSP/QST models.
- **Rule-Based Approach** – Encode complex pharmacological and biochemical processes using intuitive [rule-based modeling](https://en.wikipedia.org/wiki/Rule-based_modeling). No need to enumerate all reactions/molecular species or manually encode the corresponding network of differential equations.
- **Python-Based** – Seamlessly integrates with Python’s scientific computing ecosystem, supporting advanced simulations, data analysis, and visualization.
- **Arbitrary Number of Compartments** – Specify any number of compartments to build custom multi-compartment models, including complex drug distribution and physiologically-based pharmacokinetic (PBPK) models.
- **Enhanced reproducibility and reporting** - With built in tools like the `ModelChecker` and `ModelMetadataTracker`, you can automatically catch potential issues with model structure or components early while also tracking relevant metadata for downstream reproduction and reporting.   
- **Open-Source** - QSPy is free and open-source, meaning it is freely available and fully customizable.

------

## Key Features

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

------

## Acknowledegments

Special thanks for [Martin Breuss's MkDocs tuorial](https://realpython.com/python-project-documentation-with-mkdocs/#step-2-create-the-sample-python-package), which served as the template for setting up and generating documentation using Mkdocs.

**AI Acknowledgement**

Generative AI tools, including ChatGPT, Microsoft Copilot, and GitHub Copilot, were used to brainstorm features and implementation details, draft initial code snippets and boilerplate, and support documentation through outlining, editing, and docstring generation.