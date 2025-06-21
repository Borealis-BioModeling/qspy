from enum import Enum
from dataclasses import dataclass

TAG_SEP = "::"


def prefixer(function: str, prefix: str, sep: str = TAG_SEP):
    return "".join([prefix, sep, function])


@dataclass(frozen=True)
class FunctionalTag:
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
        return prefixer(self.function, self.class_)

    @staticmethod
    def parse(prefix_tag: str):
        class_, function = prefix_tag.split(TAG_SEP)
        return class_, function


# === Protein roles ===
PROTEIN_PREFIX = "protein"


class PROTEIN(Enum):
    LIGAND = prefixer("ligand", PROTEIN_PREFIX)
    RECEPTOR = prefixer("receptor", PROTEIN_PREFIX)
    KINASE = prefixer("kinase", PROTEIN_PREFIX)
    PHOSPHATASE = prefixer("phosphatase", PROTEIN_PREFIX)
    ADAPTOR = prefixer("adaptor", PROTEIN_PREFIX)
    TRANSCRIPTION_FACTOR = prefixer("transcription_factor", PROTEIN_PREFIX)
    ENZYME = prefixer("enzyme", PROTEIN_PREFIX)
    ANTIBODY = prefixer("antibody", PROTEIN_PREFIX)


# === Drug roles ===
DRUG_PREFIX = "drug"


class DRUG(Enum):
    SMALL_MOLECULE = prefixer("small_molecule", DRUG_PREFIX)
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
    MRNA = prefixer("mrna", RNA_PREFIX)
    miRNA = prefixer("mirna", RNA_PREFIX)
    siRNA = prefixer("sirna", RNA_PREFIX)
    lncRNA = prefixer("lncrna", RNA_PREFIX)


# === DNA roles ===
DNA_PREFIX = "dna"


class DNA(Enum):
    GENE = prefixer("gene", DNA_PREFIX)
    PROMOTER = prefixer("promoter", DNA_PREFIX)
    ENHANCER = prefixer("enhancer", DNA_PREFIX)


# === Metabolite roles ===
METABOLITE_PREFIX = "metabolite"


class METABOLITE(Enum):
    SUBSTRATE = prefixer("substrate", METABOLITE_PREFIX)
    PRODUCT = prefixer("product", METABOLITE_PREFIX)
    COFACTOR = prefixer("cofactor", METABOLITE_PREFIX)


# === Lipid roles ===
LIPID_PREFIX = "lipid"


class LIPID(Enum):
    PHOSPHOLIPID = prefixer("phospholipid", LIPID_PREFIX)
    GLYCOLIPID = prefixer("glycolipid", LIPID_PREFIX)
    STEROL = prefixer("sterol", LIPID_PREFIX)


# === Ion types ===
ION_PREFIX = "ion"


class ION(Enum):
    CALCIUM = prefixer("ca2+", ION_PREFIX)
    POTASSIUM = prefixer("k+", ION_PREFIX)
    SODIUM = prefixer("na+", ION_PREFIX)
    CHLORIDE = prefixer("cl-", ION_PREFIX)


# === Nanoparticle roles ===
NANOPARTICLE_PREFIX = "nanoparticle"


class NANOPARTICLE(Enum):
    DRUG_DELIVERY = prefixer("drug_delivery", NANOPARTICLE_PREFIX)
    THERMAL = prefixer("photothermal", NANOPARTICLE_PREFIX)
    IMAGING = prefixer("imaging", NANOPARTICLE_PREFIX)
    SENSING = prefixer("sensing", NANOPARTICLE_PREFIX)
