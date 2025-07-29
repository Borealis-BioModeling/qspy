# Getting Started with QSPy

## Installation

### Dependencies

`QSPy` has the following core dependencies:

  * [PySB](https://pysb.org/)
  * [pysb-pkpd](https://blakeaw.github.io/pysb-pkpd/)
  * [pysb-units](https://github.com/Borealis-BioModeling/pysb-units)
  * [Microbench](https://github.com/alubbock/microbench)
  * [PyViPR](https://pyvipr.readthedocs.io/en/latest/)
  * [MerGram](https://github.com/blakeaw/mergram)
  * [toml](https://github.com/uiri/toml)
  * [seaborn](https://seaborn.pydata.org/)

### Installation steps

  1. Install **PySB** using [conda](https://docs.conda.io/en/latest/) or [mamba](https://github.com/mamba-org/mamba):

```sh
conda install -c alubbock pysb
```

**OR**

```sh
mamba install -c alubbock pysb
```    

  2. Install **qspy** with pip:

```sh
pip install cueesspie
```

Ensure you have Python 3.11.3+ and PySB 1.15.0+ installed.

## Quick-start Example

```python
from qspy import *
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
    bind = (L(b=None) + R(b=None, active=False) | L(b=1) % R(b=1, active=True),
    k_f, k_r)

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
ModelChecker()

if __name___ == "__main__"
    # Generate a Markdown summary
    model.markdown_summary()
               
```