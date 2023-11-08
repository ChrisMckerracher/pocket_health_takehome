from enum import Enum
from typing import Tuple, List, Any, Union

from src.domain.dicom.tag.dicom_tag import T


class VR(Enum):
    AE = str
    AS = str
    AT = Tuple[int, int]
    CS = str
    DA = str
    DS = float
    DT = str
    FL = float
    FD = float
    IS = int
    LO = str
    LT = str
    OB = bytes
    OD = bytes
    OF = bytes
    OL = bytes
    OV = bytes
    OW = bytes
    PN = str
    SH = str
    SL = int
    SQ = List[Any]
    SS = int
    ST = str
    SV = int
    TM = str
    UC = str
    UI = str
    UL = int
    UN = bytes
    UR = str
    US = int
    UT = str
    UV = int


class ListError(Exception):
    pass


def convert(vr: VR, value: List[str]) -> T:
    """
    :param vr:
    :param value:
    :return: Converted value for any non SQ type
    """
    if not value:
        raise ListError()

    if vr is VR.SQ:
        raise AttributeError()

    vr_type = vr.value

    converted_value = [vr_type(x) for x in value]

    if len(converted_value) == 1:
        return converted_value[0]
    return converted_value
