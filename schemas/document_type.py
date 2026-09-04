from enum import Enum


class DocumentType(str, Enum):
    PASSPORT = "PASSPORT"
    DNI = "DNI"
    ACCREDITATION = "ACCREDITATION"
