# Model Summary Generator in QSPy

QSPy provides a convenient method for generating human-readable summaries of your model using the `Model.markdown_summary` function. This feature helps you document, review, and share the structure and key properties of your quantitative systems pharmacology (QSP) models.

---

## What is `Model.markdown_summary`?

The `markdown_summary` method is available on QSPy `Model` objects. It generates a Markdown summary file that includes:

- Model metadata (name, version, author, timestamp, hash)
- Monomer definitions (including sites, states, and functional tags)
- Parameters and their units
- Initial conditions
- Rules
- Observables
- (Optionally) a model diagram if the `ModelMermaidDiagram` object is included in the model definition.

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
model.markdown_summary()
```

### Custom Output Path

You can specify a custom output path for the summary file:

```python
model.markdown_summary(path="my_model_summary.md")
```

### Including a Model Diagram

If you include an instance of `ModelMermaidDiagram` in the model definition then  the corresponding diagram will be included in the summary:

```python
model.markdown_summary(include_diagram=True)
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

<!-- (Diagram would appear here if generated) -->

## Core Units
| Quantity      | Unit |
|-------------- |------|
| Concentration | nM   |
| Time          | h    |
| Volume        | L    |

## Model Component Counts
| Component Type      | Count |
|---------------------|-------|
| Monomers            | 2     |
| Parameters          | 2     |
| Expressions         | 0     |
| Compartments        | 0     |
| Rules               | 1     |
| Initial Conditions  | 2     |
| Observables         | 2     |

## Compartments
| Name  | Size |
|-------|------|
| _None_ | _N/A_ |

## Monomers
| Name | Sites   | States                      | Functional Tag      |
|------|---------|-----------------------------|---------------------|
| A    | ['b']   | {'b': ['u', 'p']}           | protein::ligand     |
| B    | []      | {}                          | protein::receptor   |

## Parameters
| Name | Value | Units |
|------|-------|-------|
| k1   | 1.0   | 1/min |
| k2   | 0.5   | 1/min |

## Expressions
| Name | Expression |
|------|------------|
| _None_ | _N/A_    |

## Initial Conditions
| Species   | Value | Units |
|-----------|-------|-------|
| A(b=None) | 100   | nM    |
| B()       | 200   | nM    |

## Rules
| Name | Rule Expression                        | k_f | k_r  | reversible |
|------|----------------------------------------|-----|------|------------|
| bind | `A(b=None) + B() >> A(b=1) % B()`      | k1  | None | False      |

## Observables
| Name     | Reaction Pattern |
|----------|------------------|
| A_total  | `A()`            |
| B_total  | `B()`            |
```

## Why Use Model Summaries?

- **Documentation**: Quickly generate a comprehensive overview of your model for reports or publications.
- **Collaboration**: Share model structure and assumptions with colleagues.
- **Reproducibility**: Archive model state and metadata alongside simulation results.

## See Also

- [Model Metadata Tracking](./metadata-tracking.md)
