"""
Functional Tagging Utilities for QSP Model Components
=====================================================

This module provides standardized functional tag definitions and utilities for
semantic annotation of model components in quantitative systems pharmacology (QSP)
models. Tags are constructed as canonical strings (e.g., "protein::ligand") that
combine a molecular class and a functional subclass, enabling consistent labeling,
introspection, and validation of model entities.

Classes and Enums
-----------------
- FunctionalTag : Dataclass for representing and parsing functional tags.
- PROTEIN       : Enum of common protein roles (e.g., ligand, receptor, kinase).
- DRUG          : Enum of drug roles (e.g., inhibitor, agonist, antibody).
- RNA           : Enum of RNA roles (e.g., messenger, micro, siRNA).
- DNA           : Enum of DNA roles (e.g., gene, promoter, enhancer).
- METABOLITE    : Enum of metabolite roles (e.g., substrate, product, cofactor).
- LIPID         : Enum of lipid roles (e.g., phospholipid, sterol).
- ION           : Enum of ion types (e.g., Ca2+, Na+, K+).
- NANOPARTICLE  : Enum of nanoparticle roles (e.g., drug delivery, imaging).

Functions
---------
- prefixer : Utility to construct canonical tag strings from class and function labels.

Examples
--------
>>> from qspy.functionaltags import FunctionalTag, PROTEIN
>>> tag = FunctionalTag("protein", "ligand")
>>> tag.value
'protein::ligand'

>>> PROTEIN.KINASE.value
'protein::kinase'

>>> FunctionalTag.parse("drug::inhibitor")
('drug', 'inhibitor')
"""

from enum import Enum
from dataclasses import dataclass

__all__ = [
    "PROTEIN",
    "DRUG",
    "RNA",
    "DNA",
    "METABOLITE",
    "ION",
    "LIPID",
    "NANOPARTICLE",
]

TAG_SEP = "::"


def prefixer(function: str, prefix: str, sep: str = TAG_SEP):
    """
    Constructs a canonical functional tag string by joining a class prefix
    and function label using the specified separator.

    This function is used to generate standardized semantic tag strings
    (e.g., "protein::ligand") for labeling model components in a consistent,
    machine-readable format.

    Parameters
    ----------
    function : str
        The functional or subclass label (e.g., "ligand").
    prefix : str
        The class or category label to prefix the function with (e.g., "protein").
    sep : str, optional
        Separator string used to join the prefix and function
        (default is `TAG_SEP`, usually "::").

    Returns
    -------
    str
        Combined class/function string (e.g., "protein::ligand").

    Examples
    --------
    >>> prefixer("regulatory", "rna")
    'rna::regulatory'

    >>> prefixer("substrate", "metabolite", sep="__")
    'metabolite__substrate'
    """

    return "".join([prefix, sep, function])


@dataclass(frozen=True)
class FunctionalTag:
    """
    Represents a functional tag for labeling monomers with semantic class/function metadata.

    A functional tag captures both a high-level molecular class (e.g., 'protein', 'rna') and a
    subclass or functional role (e.g., 'ligand', 'receptor'). These tags enable semantic annotation
    of model components to support introspection, filtering, and validation workflows.

    Parameters
    ----------
    class_ : str
        The molecular class label (e.g., 'protein').
    function : str
        The functional or subclass label (e.g., 'receptor').

    Attributes
    ----------
    value : str
        The canonical string representation of the tag (e.g., "protein__receptor").
        This is derived by prefixing the function with its class using the defined separator.

    Methods
    -------
    __eq__(other)
        Compares functional tags by class and function. Supports comparison with
        other FunctionalTag instances or Enum-based tag values.
    parse(prefix_tag : str) -> Tuple[str, str]
        Parses a canonical tag string into its (class, function) components.

    Examples
    --------
    >>> tag = FunctionalTag("protein", "ligand")
    >>> tag.value
    'protein::ligand'

    >>> FunctionalTag.parse("rna::micro")
    ('rna', 'micro')
    """

    class_: str
    function: str

    def __eq__(self, other):
        if isinstance(other, FunctionalTag):
            return (self.class_, self.function) == (other.class_, other.function)
        elif isinstance(other, Enum):
            return (self.class_, self.function) == self.parse(other.value)
        else:
            return False

    @property
    def value(self):
        """
        str: The canonical string representation of the functional tag.

        Returns the tag as a string in the format "<class>::<function>", e.g., "protein::ligand".

        Examples
        --------
        >>> tag = FunctionalTag("protein", "ligand")
        >>> tag.value
        'protein::ligand'
        """
        return prefixer(self.function, self.class_)

    @staticmethod
    def parse(prefix_tag: str):
        """
        Parse a canonical tag string into its class and function components.

        Parameters
        ----------
        prefix_tag : str
            The canonical tag string (e.g., "protein::ligand").

        Returns
        -------
        tuple of (str, str)
            The class and function components as a tuple.

        Examples
        --------
        >>> FunctionalTag.parse("protein::kinase")
        ('protein', 'kinase')
        """
        class_, function = prefix_tag.split(TAG_SEP)
        return class_, function


# === Protein roles ===
PROTEIN_PREFIX = "protein"


class PROTEIN(Enum):
    """
    Functional tag definitions for protein-based monomer classes.

    This enum provides standardized semantic tags for common protein roles
    in quantitative systems pharmacology models. Each member is constructed
    using the `prefixer` utility to combine the `PROTEIN_PREFIX` with a
    functional subclass label, producing values like "protein::ligand".

    These tags are used in monomer definitions to support validation,
    introspection, and expressive annotation of biological roles.

    Members
    -------
    LIGAND : str
        A signaling molecule that binds to a receptor.
    RECEPTOR : str
        A membrane or intracellular protein that receives ligand signals.
    KINASE : str
        An enzyme that phosphorylates other molecules.
    PHOSPHATASE : str
        An enzyme that removes phosphate groups from molecules.
    ADAPTOR : str
        A scaffold protein facilitating complex formation without enzymatic activity.
    TRANSCRIPTION_FACTOR : str
        A nuclear protein that regulates gene transcription.
    ENZYME : str
        A general-purpose catalytic protein.
    ANTIBODY : str
        An immunoglobulin capable of specific antigen binding.
    RECEPTOR_DECOY : str
        A non-signaling receptor mimic that competes with signaling receptors.

    Examples
    --------
    >>> PROTEIN.LIGAND.value
    'protein::ligand'

    >>> tag = FunctionalTag.parse(PROTEIN.KINASE.value)
    ('protein', 'kinase')
    """

    LIGAND = prefixer("ligand", PROTEIN_PREFIX)
    RECEPTOR = prefixer("receptor", PROTEIN_PREFIX)
    KINASE = prefixer("kinase", PROTEIN_PREFIX)
    PHOSPHATASE = prefixer("phosphatase", PROTEIN_PREFIX)
    ADAPTOR = prefixer("adaptor", PROTEIN_PREFIX)
    TRANSCRIPTION_FACTOR = prefixer("transcription_factor", PROTEIN_PREFIX)
    ENZYME = prefixer("enzyme", PROTEIN_PREFIX)
    ANTIBODY = prefixer("antibody", PROTEIN_PREFIX)
    RECEPTOR_DECOY = prefixer("receptor_decoy", PROTEIN_PREFIX)


# === Drug roles ===
DRUG_PREFIX = "drug"


class DRUG(Enum):
    """
    Functional tag definitions for drug-based monomer classes.

    This enum provides standardized semantic tags for common drug roles
    in quantitative systems pharmacology models. Each member is constructed
    using the `prefixer` utility to combine the `DRUG_PREFIX` with a
    functional subclass label, producing values like "drug::inhibitor".

    These tags are used in monomer definitions to support validation,
    introspection, and expressive annotation of pharmacological roles.

    Members
    -------
    SMALL_MOLECULE : str
        A low molecular weight compound, typically orally bioavailable.
    BIOLOGIC : str
        A therapeutic product derived from biological sources.
    ANTIBODY : str
        An immunoglobulin-based therapeutic.
    MAB : str
        A monoclonal antibody.
    INHIBITOR : str
        A molecule that inhibits a biological process or target.
    AGONIST : str
        A molecule that activates a receptor or pathway.
    ANTAGONIST : str
        A molecule that blocks or dampens a biological response.
    INVERSE_AGONIST : str
        A molecule that induces the opposite effect of an agonist.
    MODULATOR : str
        A molecule that modulates the activity of a target.
    ADC : str
        An antibody-drug conjugate.
    RLT : str
        A radioligand therapy agent.
    PROTAC : str
        A proteolysis targeting chimera.
    IMUNNOTHERAPY : str
        An agent used in immunotherapy.
    CHEMOTHERAPY : str
        A cytotoxic agent used in chemotherapy.

    Examples
    --------
    >>> DRUG.INHIBITOR.value
    'drug::inhibitor'

    >>> tag = FunctionalTag.parse(DRUG.ANTIBODY.value)
    ('drug', 'antibody')
    """

    SMALL_MOLECULE = prefixer("small_molecule", DRUG_PREFIX)
    BIOLOGIC = prefixer("biologic", DRUG_PREFIX)
    ANTIBODY = prefixer("antibody", DRUG_PREFIX)
    MAB = prefixer("monoclonal_antibody", DRUG_PREFIX)
    INHIBITOR = prefixer("inhibitor", DRUG_PREFIX)
    AGONIST = prefixer("agonist", DRUG_PREFIX)
    ANTAGONIST = prefixer("antagonist", DRUG_PREFIX)
    INVERSE_AGONIST = prefixer("inverse_agonist", DRUG_PREFIX)
    MODULATOR = prefixer("modulator", DRUG_PREFIX)
    ADC = prefixer("antibody_drug_conjugate", DRUG_PREFIX)
    RLT = prefixer("radioligand_therapy", DRUG_PREFIX)
    PROTAC = prefixer("protac", DRUG_PREFIX)
    IMUNNOTHERAPY = prefixer("immunotherapy", DRUG_PREFIX)
    CHEMOTHERAPY = prefixer("chemotherapy", DRUG_PREFIX)


# === RNA roles ===
RNA_PREFIX = "rna"


class RNA(Enum):
    """
    Functional tag definitions for RNA-based monomer classes.

    This enum provides standardized semantic tags for common RNA roles
    in quantitative systems pharmacology models. Each member is constructed
    using the `prefixer` utility to combine the `RNA_PREFIX` with a
    functional subclass label, producing values like "rna::micro".

    Members
    -------
    MESSENGER : str
        Messenger RNA (mRNA).
    MICRO : str
        Micro RNA (miRNA).
    SMALL_INTERFERING : str
        Small interfering RNA (siRNA).
    LONG_NONCODING : str
        Long non-coding RNA (lncRNA).

    Examples
    --------
    >>> RNA.MICRO.value
    'rna::micro'

    >>> tag = FunctionalTag.parse(RNA.MESSENGER.value)
    ('rna', 'messenger')
    """

    MESSENGER = prefixer("messenger", RNA_PREFIX)
    MICRO = prefixer("micro", RNA_PREFIX)
    SMALL_INTERFERING = prefixer("small_interfering", RNA_PREFIX)
    LONG_NONCODING = prefixer("long_noncoding", RNA_PREFIX)


# === DNA roles ===
DNA_PREFIX = "dna"


class DNA(Enum):
    """
    Functional tag definitions for DNA-based monomer classes.

    This enum provides standardized semantic tags for common DNA roles
    in quantitative systems pharmacology models. Each member is constructed
    using the `prefixer` utility to combine the `DNA_PREFIX` with a
    functional subclass label, producing values like "dna::gene".

    Members
    -------
    GENE : str
        A gene region.
    PROMOTER : str
        A promoter region.
    ENHANCER : str
        An enhancer region.

    Examples
    --------
    >>> DNA.GENE.value
    'dna::gene'

    >>> tag = FunctionalTag.parse(DNA.PROMOTER.value)
    ('dna', 'promoter')
    """

    GENE = prefixer("gene", DNA_PREFIX)
    PROMOTER = prefixer("promoter", DNA_PREFIX)
    ENHANCER = prefixer("enhancer", DNA_PREFIX)


# === Metabolite roles ===
METABOLITE_PREFIX = "metabolite"


class METABOLITE(Enum):
    """
    Functional tag definitions for metabolite-based monomer classes.

    This enum provides standardized semantic tags for common metabolite roles
    in quantitative systems pharmacology models. Each member is constructed
    using the `prefixer` utility to combine the `METABOLITE_PREFIX` with a
    functional subclass label, producing values like "metabolite::substrate".

    Members
    -------
    SUBSTRATE : str
        A substrate molecule in a metabolic reaction.
    PRODUCT : str
        A product molecule in a metabolic reaction.
    COFACTOR : str
        A cofactor required for enzyme activity.

    Examples
    --------
    >>> METABOLITE.SUBSTRATE.value
    'metabolite::substrate'

    >>> tag = FunctionalTag.parse(METABOLITE.PRODUCT.value)
    ('metabolite', 'product')
    """

    SUBSTRATE = prefixer("substrate", METABOLITE_PREFIX)
    PRODUCT = prefixer("product", METABOLITE_PREFIX)
    COFACTOR = prefixer("cofactor", METABOLITE_PREFIX)


# === Lipid roles ===
LIPID_PREFIX = "lipid"


class LIPID(Enum):
    """
    Functional tag definitions for lipid-based monomer classes.

    This enum provides standardized semantic tags for common lipid roles
    in quantitative systems pharmacology models. Each member is constructed
    using the `prefixer` utility to combine the `LIPID_PREFIX` with a
    functional subclass label, producing values like "lipid::phospholipid".

    Members
    -------
    PHOSPHOLIPID : str
        A phospholipid molecule.
    GLYCOLIPID : str
        A glycolipid molecule.
    STEROL : str
        A sterol molecule.
    EICOSANOID : str
        An eicosanoid molecule.

    Examples
    --------
    >>> LIPID.PHOSPHOLIPID.value
    'lipid::phospholipid'

    >>> tag = FunctionalTag.parse(LIPID.STEROL.value)
    ('lipid', 'sterol')
    """

    PHOSPHOLIPID = prefixer("phospholipid", LIPID_PREFIX)
    GLYCOLIPID = prefixer("glycolipid", LIPID_PREFIX)
    STEROL = prefixer("sterol", LIPID_PREFIX)
    EICOSANOID = prefixer("eicosanoid", LIPID_PREFIX)


# === Ion types ===
ION_PREFIX = "ion"


class ION(Enum):
    """
    Functional tag definitions for ion-based monomer classes.

    This enum provides standardized semantic tags for common ion types
    in quantitative systems pharmacology models. Each member is constructed
    using the `prefixer` utility to combine the `ION_PREFIX` with a
    functional subclass label, producing values like "ion::ca2+".

    Members
    -------
    CALCIUM : str
        Calcium ion (Ca2+).
    POTASSIUM : str
        Potassium ion (K+).
    SODIUM : str
        Sodium ion (Na+).
    CHLORIDE : str
        Chloride ion (Cl-).
    MAGNESIUM : str
        Magnesium ion (Mg2+).

    Examples
    --------
    >>> ION.CALCIUM.value
    'ion::ca2+'

    >>> tag = FunctionalTag.parse(ION.SODIUM.value)
    ('ion', 'na+')
    """

    CALCIUM = prefixer("ca2+", ION_PREFIX)
    POTASSIUM = prefixer("k+", ION_PREFIX)
    SODIUM = prefixer("na+", ION_PREFIX)
    CHLORIDE = prefixer("cl-", ION_PREFIX)
    MAGNESIUM = prefixer("mg2+", ION_PREFIX)


# === Nanoparticle roles ===
NANOPARTICLE_PREFIX = "nanoparticle"


class NANOPARTICLE(Enum):
    """
    Functional tag definitions for nanoparticle-based monomer classes.

    This enum provides standardized semantic tags for common nanoparticle roles
    in quantitative systems pharmacology models. Each member is constructed
    using the `prefixer` utility to combine the `NANOPARTICLE_PREFIX` with a
    functional subclass label, producing values like "nanoparticle::imaging".

    Members
    -------
    DRUG_DELIVERY : str
        Nanoparticle for drug delivery.
    THERMAL : str
        Photothermal nanoparticle.
    IMAGING : str
        Nanoparticle for imaging.
    SENSING : str
        Nanoparticle for sensing.
    THERANOSTIC : str
        Theranostic nanoparticle.

    Examples
    --------
    >>> NANOPARTICLE.DRUG_DELIVERY.value
    'nanoparticle::drug_delivery'

    >>> tag = FunctionalTag.parse(NANOPARTICLE.IMAGING.value)
    ('nanoparticle', 'imaging')
    """

    DRUG_DELIVERY = prefixer("drug_delivery", NANOPARTICLE_PREFIX)
    THERMAL = prefixer("photothermal", NANOPARTICLE_PREFIX)
    IMAGING = prefixer("imaging", NANOPARTICLE_PREFIX)
    SENSING = prefixer("sensing", NANOPARTICLE_PREFIX)
    THERANOSTIC = prefixer("theranostic", NANOPARTICLE_PREFIX)


# # === Rate constant orders ===
# RATE_PREFIX = "rate_constant"


# class RATE(Enum):
#     """
#     Functional tag definitions for kinetic rate types.

#     This enum provides standardized semantic tags for common kinetic rate orders
#     in quantitative systems pharmacology models. Each member is constructed
#     using the `prefixer` utility to combine the `RATE_PREFIX` with a
#     rate order label, producing values like "rate_constant::first-order".

#     Members
#     -------
#     ZERO : str
#         Zero-order rate constant (rate independent of concentration).
#     FIRST : str
#         First-order rate constant (rate proportional to one reactant).
#     SECOND : str
#         Second-order rate constant (rate proportional to two reactants).

#     Examples
#     --------
#     >>> RATE.FIRST.value
#     'rate_constant::first-order'

#     >>> tag = FunctionalTag.parse(RATE.SECOND.value)
#     ('rate_constant', 'second-order')
#     """

#     ZERO = prefixer("zero-order", RATE_PREFIX)
#     FIRST = prefixer("first-order", RATE_PREFIX)
#     SECOND = prefixer("second-order", RATE_PREFIX)
