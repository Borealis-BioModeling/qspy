---
icon: material/home
---

# QSPy: Quantitative Systems Pharmacology in Python

![QSPy logo](./assets/qspy-logo-plain.svg){ width="200" }


`QSPy` (pronounced _"Cue Ess Pie"_) is a [Python](https://www.python.org/) framework for building modular, rule-based models that describe drug behavior and pharmacological interactions within biological systems. Leveraging the power of [PySB](https://pysb.org/), it streamlines the development, simulation, and analysis of **quantitative systems pharmacology (QSP)** models through a reproducible and programmatic approach.

------

[ Getting Started ](./getting-started.md){ .md-button .md-button--primary } [How-To Guides](./how-to-guides.md){ .md-button .md-button--primary } [Build Model](./model-specification.md){ .md-button .md-button--primary } [Share Model](https://github.com/Borealis-BioModeling/qspy/discussions/2){ .md-button .md-button--primary }

[API Documentation](./reference.md){ .md-button .md-button--primary } [  Need Help?  ](./contact-support.md){ .md-button .md-button--primary } [About QSPy](./about-qspy.md){ .md-button .md-button--primary } [Contributing](./contributing.md){ .md-button .md-button--primary }

------

------
 

![QSPy logo](./assets/navig-8_hey-listen.svg){ width="150" }
!!! quote "Navig-8 says:"
    Thanks for exploring QSPy! This project is still in early development, so your feedback and support are especially important. You can help us continue to make QSPy better! 

[Leave Feedback](https://app.gitter.im/#/room/#qspy-feedback:gitter.im){ .md-button .md-button--primary } [Other Ways to Support the Project](./supporting.md){ .md-button .md-button--primary }

------

[![PySB version badge](https://img.shields.io/badge/powered_by-PySB-9cf.svg?logo=data:image/svg%2bxml;base64,PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0iVVRGLTgiIHN0YW5kYWxvbmU9Im5vIj8+CjwhLS0gQ3JlYXRlZCB3aXRoIElua3NjYXBlIChodHRwOi8vd3d3Lmlua3NjYXBlLm9yZy8pIC0tPgoKPHN2ZwogICB3aWR0aD0iMjEuNDk2MzNtbSIKICAgaGVpZ2h0PSIzMC4zNjU5MDRtbSIKICAgdmlld0JveD0iMCAwIDIxLjQ5NjMzIDMwLjM2NTkwNCIKICAgdmVyc2lvbj0iMS4xIgogICBpZD0ic3ZnMSIKICAgeG1sOnNwYWNlPSJwcmVzZXJ2ZSIKICAgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIgogICB4bWxuczpzdmc9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZGVmcwogICAgIGlkPSJkZWZzMSIgLz48ZwogICAgIGlkPSJsYXllcjEiCiAgICAgdHJhbnNmb3JtPSJ0cmFuc2xhdGUoLTk4LjkxMTA2OSwtMTAwLjIzOTA5KSI+PHBhdGgKICAgICAgIHN0eWxlPSJmaWxsOiMzN2FiYzgiCiAgICAgICBkPSJtIDEwNy44MjksMTI5LjkxMTE5IGMgLTQuMDY1NzUsLTIuOTQ2MzIgLTcuNjYwNjEsLTcuMDczOTYgLTguNTc4NTU4LC0xMi4xNDc2MSAtMC40ODMwMjYsLTIuNzA5NTQgLTAuNTU0MTkzLC01LjU0MTA3IDAuMDUxNDUsLTguMjM0NTcgMS4wMTYzODgsLTMuOTk0MjggMy43OTU1MzgsLTcuOTY0MTEgNy45ODk5ODgsLTguOTcwOTggMy4xMjYxMSwtMC43MzI2NzIgNi43MjI0MiwtMC40NDA4NyA5LjI5MzIxLDEuNjQ3NzEgMi44MzA3MSwyLjEzOTQ2IDQuMzYxNjMsNS44NjIzNSAzLjcxNTc5LDkuMzcwMjUgLTAuNDUxMjEsMy4yNzQ4IC0yLjk5NTMzLDYuMTU1MDggLTYuMjQyMTQsNi44NjgyOCAtMi44NjExNCwwLjcxNjk4IC02LjE3OTEzLC0wLjM4NDcyIC03LjcyNTk5LC0yLjk3NjEzIC0xLjU1NzgsLTIuNDA3NTQgLTEuMzAwODksLTYuMDU5NDMgMS4xNDk5NiwtNy43ODczNCAyLjAyNTczLC0xLjUyNTQ3IDUuNDYzNzIsLTEuNDQxMzUgNi45MDEyNCwwLjg0MzkxIDAuOTMzOTgsMS42MjM4MiAtMC4xMjAyMyw0LjEwOTgxIC0yLjA5MTE4LDQuMjA4MDYgLTEuMzQwNDEsLTAuMjI4MDUgLTIuODU4MTYsLTIuMTQ3NDcgLTQuMDgxNzIsLTAuNTQwNDEgLTAuODMzMjcsMS4yODYzNyAwLjI0MTE3LDIuOTEyNDMgMS40NzAxOSwzLjQ2ODQxIDIuNjU3NCwxLjQ0MjAxIDYuMDI5MjMsLTAuMDY1NyA3LjUxNjk5LC0yLjUwMzI3IDEuMjE0NjUsLTEuNzk5OTUgMS40MzY2MywtNC4yODExNSAwLjI1OTI1LC02LjE1NzgyIC0xLjE0MjIsLTIuMjQ1MTcgLTMuNTk0OTYsLTMuODA5ODcgLTYuMTQ1ODksLTMuNjIwNjEgLTIuMTAxMzksLTAuMTMwNDUgLTQuNDAyOTQsMC4wNjgxIC02LjAzOTI5LDEuNTQ2NDggLTIuMDA3MzYsMS41MDE1OSAtMy40MTM0MSwzLjg4NTM0IC0zLjMzMTEsNi40Mzg5IC0wLjE3NTcsMi4zMjc5NyAwLjI0ODQ3LDQuNzk3MDUgMS43OTI4Miw2LjYyODQzIDEuMzg3NjgsMS43ODc5NCAzLjM1Njk0LDMuMDM2NTcgNS40MzAwNSwzLjg4ODczIDEuMDE0ODQsMS41NzE5NCAwLjcwMTI1LDEuOTc4NzMgMS4wNTIwOCwzLjcxMTA3IC0wLjEzNDAyLDEuMDAxNzggLTAuMjk5MzMsNC42ODgxNyAtMS4zNjI5NCw0Ljg5MzE3IC0wLjM3MDMsLTAuMTM4MDUgLTAuNjYwODMsLTAuNDIzMDggLTEuMDI0MjEsLTAuNTc0NjYgeiIKICAgICAgIGlkPSJwYXRoMiIgLz48L2c+PC9zdmc+Cg==)](https://pysb.org/)