# Functional Tags for Monomers in QSPy

In QSPy, functional tags annotate **monomers** with biologically or computationally meaningful labels. These tags express a **class/function** relationship—such as marking a species as a `receptor`, adding additional expressiveness to model species while also supporting another way to filter monomers.

---

## Tagging Semantics

- Tags indicate **class** and **function/subclass** roles.
- Each monomer can have a **single tag**.
- Tags improve:
  - Model expressiveness
  - Filtering by biological function

Functional tags are in all caps and have the following pattern in model definitions:

    CLASS.FUNCTION

### Python Example

```python
    with monomers():
        drug = (['b'], None, DRUG.INHIBITOR)
```

Functional tags are accesible by a monomer's `functional_tag` attribute:

```python
>>> print(drug.functional_tag)
```

    FunctionalTag(class_='drug', function='inhibitor')

---

## Recognized Classes and Functions

The table below lists standardized tags currently used in QSPy.

| **Class Tag**  | **Function/Subclass**                                                                                                                                                          | **Description**                                                                                                        |
| -------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------- |
| `DRUG`         | `SMALL_MOLECULE`, `BIOLOGIC`, `ANTIBODY`, `MAB`, `INHIBITOR`, `AGONIST`, `ANTAGONIST`, `INVERSE_AGONIST`, `MODULATOR`, `ADC`, `RLT`, `PROTAC`, `IMMUNOTHERAPY`, `CHEMOTHERAPY` | Therapeutic agents                                                                                                     |
| `PROTEIN`      | `LIGAND`, `RECEPTOR`, `RECEPTOR_DECOY`, `KINASE`, `PHOSPHATASE`, `ADAPTOR`, `TRANSCRIPTION_FACTOR`, `ENZYME`, `ANTIBODY`                                                       | Biologically active protein-based macromolecules                                                                       |
| `RNA`          | `MESSENGER`, `MICRO`, `SMALL_INTERFERING`, `LONG_NONCODING`                                                                                                                    | Transcribed nucleic acids involved in gene expression, regulation, or signal propagation                               |
| `METABOLITE`   | `SUBSTRATE`, `PRODUCT`, `COFACTOR`                                                                                                                                             | Small molecules involved in biochemical reactions, such as intermediates, reactants, and regulatory modulators         |
| `LIPID`        | `EICOSANOID`, `PHOSPHOLIPID`, `GLYCOLIPID`, `STEROL`                                                                                                                           | Hydrophobic or amphipathic molecules involved in signaling or other biological functions                               |
| `ION`          | `CALCIUM`, `CHLORIDE`, `MAGNESIUM`, `SODIUM`, `POTASSIUM`                                                                                                                      | Charged atoms or small molecules involved in electrochemical signaling, osmotic balance, and catalysis                 |
| `NANOPARTICLE` | `DRUG_DELIVERY`, `IMAGING`, `SENSING`, `THERMAL`, `THERANOSTIC`                                                                                                                | Engineered nanoscale particles designed for targeted delivery, imaging enhancement, or localized therapeutic functions |

## Custom tags

Users can define custom tags. For consistency, follow the schema above when possible.

Functional tags are subclasses of the `enum.Enum` object and can be defined as below:

```python
from enum import Enum
from qspy.functionaltags import prefixer

MY_TAG_PREFIX = "mytag"
class MY_TAG(Enum):
    FUNCTION = prefixer("function", MY_TAG_PREFIX)
    SUBCLASS = prefixer("subclass", MY_TAG_PREFIX)
```

Then, you can use the custom tag like any other:

```python
with monomers():
    A = (None, None, MY_TAG.FUNCTION)

Monomer('B') @ MY_TAG.SUBCLASS
```

---
