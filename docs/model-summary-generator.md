# Model Summary Generator in QSPy

QSPy provides a convenient method for generating human-readable summaries of your model using the `Model.summarize` function. This feature helps you document, review, and share the structure and key properties of your quantitative systems pharmacology (QSP) models.

---

## What is `Model.summarize`?

The `summarize` method is available on QSPy `Model` objects. It generates a Markdown summary file that includes:

- Model metadata (name, version, author, timestamp, hash)
- Monomer definitions (including sites, states, and functional tags)
- Parameters and their units
- Initial conditions
- Rules
- Observables
- (Optionally) a model diagram if SBMLDiagrams is available

This summary is useful for documentation, collaboration, and reproducibility.

---

## Usage

### Basic Example

```python
from qspy.core import Model

# Build your model here...

model = Model().with_units(...)
# ... define monomers, parameters, rules, etc.

# Generate a summary file (default location: SUMMARY_DIR)
model.summarize()
```

### Custom Output Path

You can specify a custom output path for the summary file:

```python
model.summarize(path="my_model_summary.md")
```

### Including a Model Diagram

If you have SBMLDiagrams installed, you can include a diagram in the summary:

```python
model.summarize(include_diagram=True)
```

## Example Output

A generated summary file (Markdown) will look like:

```markdown
# QSPy Model Summary: `MyModel`

**Model name**: `MyModel`  
**Hash**: `abcd1234`  
**Version**: 1.0.0  
**Author**: Alice  
**Executed by**: alice  
**Timestamp**: 2025-07-02T12:34:56

## 🖼️ Model Diagram

![Model Diagram](.qspy/model_diagram.png)

## Monomers

- `A` with sites `['b']` and states `{'b': ['u', 'p']}` and CLASS::FUNCTION `protein::ligand`
- `B` with sites `[]` and states `{}` and CLASS::FUNCTION `protein::receptor`

## Parameters

| Name | Value | Units |
| ---- | ----- | ----- |
| k1   | 1.0   | 1/min |
| k2   | 0.5   | 1/min |

## Initial Conditions

| Species   | Value | Units |
| --------- | ----- | ----- |
| A(b=None) | 100   | nM    |
| B()       | 200   | nM    |

## Rules

- `Rule('bind', A(b=None) + B() >> A(b=1) % B(), k1)`

## Observables

- `A_total`
- `B_total`
```

## Why Use Model Summaries?

- **Documentation**: Quickly generate a comprehensive overview of your model for reports or publications.
- **Collaboration**: Share model structure and assumptions with colleagues.
- **Reproducibility**: Archive model state and metadata alongside simulation results.

## See Also

- [Model Metadata Tracking](./metadata-tracking.md)
