# QSPy: Quantitative Systems Pharmacology in Python

![img](./docs/assets/qspy-logo.png)

QSPy ('Cue Ess Pie') is a Python-based framework for the programmatic construction of rule-based mathematical models that describe drugs and their interactions with biological systems. Built on [PySB](https://pysb.org/), it enables modular modeling and simulation of quantitative systems pharmacology (QSP) models. 

[![Project Status: WIP – Initial development is in progress, but there has not yet been a stable, usable release suitable for the public.](https://www.repostatus.org/badges/latest/wip.svg)](https://www.repostatus.org/#wip)
![Python version badge](https://img.shields.io/badge/python-3.11.9-blue.svg)
[![PySB version badge](https://img.shields.io/badge/powered_by-PySB>%3D1.15.0-9cf.svg?logo=data:image/svg%2bxml;base64,PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0iVVRGLTgiIHN0YW5kYWxvbmU9Im5vIj8+CjwhLS0gQ3JlYXRlZCB3aXRoIElua3NjYXBlIChodHRwOi8vd3d3Lmlua3NjYXBlLm9yZy8pIC0tPgoKPHN2ZwogICB3aWR0aD0iMjEuNDk2MzNtbSIKICAgaGVpZ2h0PSIzMC4zNjU5MDRtbSIKICAgdmlld0JveD0iMCAwIDIxLjQ5NjMzIDMwLjM2NTkwNCIKICAgdmVyc2lvbj0iMS4xIgogICBpZD0ic3ZnMSIKICAgeG1sOnNwYWNlPSJwcmVzZXJ2ZSIKICAgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIgogICB4bWxuczpzdmc9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZGVmcwogICAgIGlkPSJkZWZzMSIgLz48ZwogICAgIGlkPSJsYXllcjEiCiAgICAgdHJhbnNmb3JtPSJ0cmFuc2xhdGUoLTk4LjkxMTA2OSwtMTAwLjIzOTA5KSI+PHBhdGgKICAgICAgIHN0eWxlPSJmaWxsOiMzN2FiYzgiCiAgICAgICBkPSJtIDEwNy44MjksMTI5LjkxMTE5IGMgLTQuMDY1NzUsLTIuOTQ2MzIgLTcuNjYwNjEsLTcuMDczOTYgLTguNTc4NTU4LC0xMi4xNDc2MSAtMC40ODMwMjYsLTIuNzA5NTQgLTAuNTU0MTkzLC01LjU0MTA3IDAuMDUxNDUsLTguMjM0NTcgMS4wMTYzODgsLTMuOTk0MjggMy43OTU1MzgsLTcuOTY0MTEgNy45ODk5ODgsLTguOTcwOTggMy4xMjYxMSwtMC43MzI2NzIgNi43MjI0MiwtMC40NDA4NyA5LjI5MzIxLDEuNjQ3NzEgMi44MzA3MSwyLjEzOTQ2IDQuMzYxNjMsNS44NjIzNSAzLjcxNTc5LDkuMzcwMjUgLTAuNDUxMjEsMy4yNzQ4IC0yLjk5NTMzLDYuMTU1MDggLTYuMjQyMTQsNi44NjgyOCAtMi44NjExNCwwLjcxNjk4IC02LjE3OTEzLC0wLjM4NDcyIC03LjcyNTk5LC0yLjk3NjEzIC0xLjU1NzgsLTIuNDA3NTQgLTEuMzAwODksLTYuMDU5NDMgMS4xNDk5NiwtNy43ODczNCAyLjAyNTczLC0xLjUyNTQ3IDUuNDYzNzIsLTEuNDQxMzUgNi45MDEyNCwwLjg0MzkxIDAuOTMzOTgsMS42MjM4MiAtMC4xMjAyMyw0LjEwOTgxIC0yLjA5MTE4LDQuMjA4MDYgLTEuMzQwNDEsLTAuMjI4MDUgLTIuODU4MTYsLTIuMTQ3NDcgLTQuMDgxNzIsLTAuNTQwNDEgLTAuODMzMjcsMS4yODYzNyAwLjI0MTE3LDIuOTEyNDMgMS40NzAxOSwzLjQ2ODQxIDIuNjU3NCwxLjQ0MjAxIDYuMDI5MjMsLTAuMDY1NyA3LjUxNjk5LC0yLjUwMzI3IDEuMjE0NjUsLTEuNzk5OTUgMS40MzY2MywtNC4yODExNSAwLjI1OTI1LC02LjE1NzgyIC0xLjE0MjIsLTIuMjQ1MTcgLTMuNTk0OTYsLTMuODA5ODcgLTYuMTQ1ODksLTMuNjIwNjEgLTIuMTAxMzksLTAuMTMwNDUgLTQuNDAyOTQsMC4wNjgxIC02LjAzOTI5LDEuNTQ2NDggLTIuMDA3MzYsMS41MDE1OSAtMy40MTM0MSwzLjg4NTM0IC0zLjMzMTEsNi40Mzg5IC0wLjE3NTcsMi4zMjc5NyAwLjI0ODQ3LDQuNzk3MDUgMS43OTI4Miw2LjYyODQzIDEuMzg3NjgsMS43ODc5NCAzLjM1Njk0LDMuMDM2NTcgNS40MzAwNSwzLjg4ODczIDEuMDE0ODQsMS41NzE5NCAwLjcwMTI1LDEuOTc4NzMgMS4wNTIwOCwzLjcxMTA3IC0wLjEzNDAyLDEuMDAxNzggLTAuMjk5MzMsNC42ODgxNyAtMS4zNjI5NCw0Ljg5MzE3IC0wLjM3MDMsLTAuMTM4MDUgLTAuNjYwODMsLTAuNDIzMDggLTEuMDI0MjEsLTAuNTc0NjYgeiIKICAgICAgIGlkPSJwYXRoMiIgLz48L2c+PC9zdmc+Cg==)](https://pysb.org/)
[![license](https://img.shields.io/github/license/Borealis-BioModeling/qspy.svg)](LICENSE)
[![release](https://img.shields.io/github/release-pre/Borealis-BioModeling/qspy.svg)](https://github.com/Borealis-BioModeling/qspy/releases)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
![Static Badge](https://img.shields.io/badge/coverage-56%25-green)
[![CI](https://github.com/Borealis-BioModeling/qspy/actions/workflows/ruff.yml/badge.svg)](https://github.com/Borealis-BioModeling/qspy/actions/workflows/ruff.yml)
[![Static Badge](https://img.shields.io/badge/documentation-borealis--biomodeling.github.io/qspy/-blue?link=https://borealis-biomodeling.github.io/qspy/)](https://borealis-biomodeling.github.io/qspy/)



  :pill: :computer:

## What's new in

**version 0.1.0**

 * First release!

## Table of Contents

 1. [Install](#install)
     1. [Dependencies](#dependencies)
     2. [pip install](#pip-install)
     3. [Manual install](#manual-install)
 2. [License](#license)
 3. [Change Log](#change-log)
 4. [Documentation and Usage](#documentation-and-usage)
     1. [Quick Overview](#quick-overview)
     2. [Example](#example)
 5. [Contact](#contact)
 6. [Contributing](#contributing)
 7. [Supporting](#supporting)  
 8. [Other Useful Tools](#other-useful-tools)

------

# Install

| **! Note** |
| :--- |
|  qspy is still in version zero development so new versions may not be backwards compatible. |

**qspy** has been developed with Python 3.11.9 and PySB 1.15.0.

## Dependencies

`QSPy` has the following core dependencies:

  * [PySB](https://pysb.org/)
  * [pysb-pkpd](https://blakeaw.github.io/pysb-pkpd/)
  * [pysb-units](https://github.com/Borealis-BioModeling/pysb-units)
  * [Microbench](https://github.com/alubbock/microbench)
  * [PyViPR](https://pyvipr.readthedocs.io/en/latest/)
  * [MerGram](https://github.com/blakeaw/mergram)

## Installation
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

### Testing and Coverage

For automated testing and coverage analysis:
   * [pytest](https://docs.pytest.org/en/stable/getting-started.html)
   * [Coverage.py](https://coverage.readthedocs.io/en/7.6.10/install.html)
   * [nose](https://nose.readthedocs.io/en/latest/)
```
pip install pytest coverage nose
```

------

# License

This project is licensed under the BSD 2-Clause License - see the [LICENSE](LICENSE) file for details

------

# Change Log

See: [CHANGELOG](CHANGELOG.md)

------

# Documentation and Usage

Full documentation is available at:

[https://borealis-biomodeling.github.io/qspy/](https://borealis-biomodeling.github.io/qspy/) 

Built With:

[![Built with Material for MkDocs](https://img.shields.io/badge/Material_for_MkDocs-526CFE?style=for-the-badge&logo=MaterialForMkDocs&logoColor=white)](https://squidfunk.github.io/mkdocs-material/)

### Quick Start Example

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
ModelChecker()

# Generate a Markdown summary of the model
model.markdown_summary()
               
```

------

# Contact

 * **Issues** :bug: : Please open a [GitHub Issue](https://github.com/Borealis-BioModeling/qspy/issues) to
report any problems/bugs with the code or its execution, or to make any feature requests.
 * **Discussions** :grey_question: : If you have questions, suggestions, or want to discuss anything else related to the project, feel free to use the [Discussions](https://github.com/Borealis-BioModeling/qspy/discussions) board.
* **Support** :question: : For any other support inquiries you can send an email to [blakeaw1102@gmail.com](mailto:blakeaw1102@gmail.com).

------

# Contributing

Interested in contributing to this project? See [CONTRIBUTING](./CONTRIBUTING.md) for details.

------

# Supporting

I'm very happy that you've chosen to use __qspy__. This add-on is a project that I develop and maintain on my own time, independently of the core PySB library, and without external funding. If you've found it helpful, here are a few ways you can support its ongoing development:

* **Star** :star: : Show your support by starring the [GitHub repository](https://github.com/Borealis-BioModeling/qspy). It helps increase the project's visibility and lets others know it's useful. It also benefits my motivation to continue improving the package!
* **Share** :mega: : Sharing `qspy` on your social media, forums, or with your network is another great way to support the project. It helps more people discover `qspy`, which in turn motivates me to keep developing!
* **Cite** :books: : Citing or mentioning this software in your work, publications, or projects is another valuable way to support it. It helps spread the word and acknowledges the effort put into its development, which is greatly appreciated!
* **Sponsor** :dollar: : Even small financial contributions, such as spotting me the cost of a tea through Ko-fi so I can get my caffeine fix, can make a big difference! Every little bit can help me continue developing this and other open-source projects. 

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/J3J4ZUCVU)

-----

# Acknowledegments

Special thanks for [Martin Breuss's MkDocs tuorial](https://realpython.com/python-project-documentation-with-mkdocs/#step-2-create-the-sample-python-package), which served as the template for setting up and generating documentation using Mkdocs.

**AI Acknowledgement**

This package was developed with AI assistance. This inlcudes the generative AI tools ChatGPT, Microsoft Copilot, and GitHub Copilot, which were used to brainstorm features and implementation details, draft initial code snippets and boilerplate, and support documentation through outlining, editing, and docstring generation.

-----