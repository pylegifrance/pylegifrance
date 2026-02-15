from enum import Enum

from pylegifrance.models.generated.model import Sort1 as _Sort


class Sort(Enum):
    """Sort parameter for search fond LODA"""

    PUBLICATION_DATE_ASC = _Sort.publication_date_asc.value
    PUBLICATION_DATE_DESC = _Sort.publication_date_desc.value
    SIGNATURE_DATE_DESC = _Sort.signature_date_desc.value
    SIGNATURE_DATE_ASC = _Sort.signature_date_asc.value
    ID_ASC = _Sort.id_asc.value
    ID_DESC = _Sort.id_desc.value
