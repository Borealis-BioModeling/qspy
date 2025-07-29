# Experimental Features in QSPy

The `qspy.experimental` module provides early-access APIs and advanced modeling features that are not yet part of the stable QSPy release. These features are intended for prototyping and feedback. Please try them out and let us know what you think!

!!! warning
    Experimental features may not be stable or properly tested. They may also change dramatically or be removed in future versions.

---

## Overview

Experimental features in QSPy include:

- **Functional Monomers:** Classes, mixins, protein-specific monomers, and advanced macros for building and manipulating functional monomers.
- **Infix Macros:** Expressive infix-style macros for model specification, enabling readable code for binding, elimination, and equilibrium reactions.

---

## Functional Monomers

Located in `qspy.experimental.functional_monomers`, this subpackage provides:

- `FunctionalMonomer`: Base class for monomers with functional tags and base states.
- Mixins for binding (`BindMixin`), synthesis (`SynthesizeMixin`), and degradation (`DegradeMixin`).

### Protein-Specific Classes

- `Ligand`: Class for ligand monomers with binding functionality.
- `Receptor`: Class for receptor monomers with orthosteric/allosteric binding and activation logic.

**Example:**
```python
from qspy.experimental.functional_monomers.protein import Ligand, Receptor

lig = Ligand("LigandA")
rec = Receptor("ReceptorA")

# Define binding and turnover reactions
lig.binds_to(rec, "b_ortho", k_f, k_r)
rec.turnover(k_syn, k_deg)
```

### Advanced Macros

- `activate_concerted`: For concerted activation of a receptor by a ligand, combining binding and state change in one step.

**Example:**
```python
from qspy.experimental.functional_monomers.macros import activate_concerted

activate_concerted(
    ligand, "b", receptor, "b",
    {"state": "inactive"}, {"state": "active"},
    [k_f, k_r]
)
```

---

## Infix Macros

Located in `qspy.experimental.infix_macros`, these macros allow for expressive, readable model code using infix-like chemical/biological/pharmcological operators:

- `*binds*`: For reversible binding reactions.
- `*eliminated*`: For elimination reactions.
- `*equilibrates*`: For reversible state transitions.

**Example:**
```python
from qspy.experimental.infix_macros import binds, eliminated, equilibrates

# Reversible binding
species1 *binds* species2 @ ('binding_site1', 'binding_site2') & (k_f, k_r)
## OR
species1(binding_site1=None) *binds* species2(binding_site2=None) & (k_f, k_r)

# Elimination
species *eliminated* compartment & k_elim

# State equilibrium
state1 *equilibrates* state2 & (k_f, k_r)
```

---

## Usage Notes

- **API Stability:** Experimental features may change without notice. Use with caution in production models.
- **Feedback:** User feedback is welcome! Please report issues or suggestions to the QSPy development team.
- **Documentation:** Experimental features may have limited documentation. Refer to source code and docstrings for details.

---

## How to Import

Experimental features are not imported by default. You must explicitly import them from the `qspy.experimental` namespace:

```python
from qspy.experimental.infix_macros import binds, eliminated
from qspy.experimental.functional_monomers.protein import Ligand, Receptor
```

---

## Contributing

We want to know how useful these experimental features are, and how well they work with your modeling workflows. So, please try them out and let us know what you think through any of our [contact/support channels](./contact-support.md), and you can report any functional issues using the GitHub Issue tracker.

If you have ideas for new experimental features, please reach out to share your ideas, or see our [Contributing Guidelines](./contributing.md) if you want to contribute code. 

---
