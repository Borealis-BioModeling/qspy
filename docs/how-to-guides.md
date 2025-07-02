# How-To Guides

## How to Simulate a Model

`qspy` provides a `simulate` function that can be used to easily
execute a dynamic ODE-based simulation of your QSP model as below:

```python
import numpy as np
from qspy import simulate
from my_qsp_model import model

# Simulate the QSP/PKPD/PySB model.
## Set the timespan for the simulation:
tspan = np.arange(241) # 0-240 seconds at 1 second intervals
## Execute the simulation:
simulation_trajectory = simulate(model, tspan)
```

## How to filter a model's monomers by functional tag

```python
from qspy.functionaltags import *
from my_qsp_model import model

# Get all the monomers tagged as protein receptors
receptors = model.monomers.filter(lambda m: m.functional_tag == PROTEIN.RECEPTOR)
# Get all the monomers tagged as inhibitor drugs
inhibitors = model.monomers.filter(lambda m: m.functional_tag == DRUG.INHIBITOR)
```

## How to define custom monomer functional tags

See [Functional Tags: Custom Tags](./functional-tags.md#custom-tags)

## 🚧 Page Still Under Development 🚧

Thank you for your interest in our **How-To Guides** section! We’re actively working on expanding these pages to provide **step-by-step instructions** and **hands-on examples** for using `qspy`.

Our goal is to make these resources **clear, practical, and easy to follow**—but we’re still in the process of gathering content and refining details.

Stay tuned! In the meantime:

- **Have a specific question?** Feel free to explore our existing documentation or reach out to the community.
- **Want to contribute?** If you have suggestions or example workflows, we'd love to hear from you!

Check back soon for updates as we continue to improve these guides!
