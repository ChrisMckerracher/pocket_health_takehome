from enum import Enum
from typing import Any, Optional, Union, List, ForwardRef, Generic, TypeVar

from pydantic import BaseModel
from pydicom.tag import BaseTag

partial_T= Union[str, int, float, bytes, List[ForwardRef("DicomTag[Any]")]]
T = TypeVar("T", bound=Union[partial_T, List[partial_T]])

class TagMap(Enum):
    pass
    # "00010002" = (vr,name)


class DicomTag(BaseModel, Generic[T]):
    group_id: int
    element_id: int
    vr: str
    name: str
    value: T


tag = DicomTag["List[List[DicomTag]]"](group_id=8, element_id=4416, name="Referenced Image Sequence", vr="SQ", value=[
    [
        DicomTag[str](group_id=8, element_id=4432, name="Referenced SOP Class UID", vr="UI",
                 value='1.2.840.10008.5.1.4.1.1.4'),
        DicomTag[str](group_id=8, element_id=4437, name="Referenced SOP Instance UID", vr="UI",
                 value='1.3.12.2.1107.5.2.6.24119.30000013121716094326500000391')
    ],
    [
        DicomTag[str](group_id=8, element_id=4432, name="Referenced SOP Class UID", vr="UI",
                 value='1.2.840.10008.5.1.4.1.1.4'),
        DicomTag[str](group_id=8, element_id=4437, name="Referenced SOP Instance UID", vr="UI",
                 value='1.3.12.2.1107.5.2.6.24119.30000013121716094326500000392')
    ],
    [
        DicomTag(group_id=8, element_id=4432, name="Referenced SOP Class UID", vr="UI",
                 value='1.2.840.10008.5.1.4.1.1.4'),
        DicomTag(group_id=8, element_id=4437, name="Referenced SOP Instance UID", vr="UI",
                 value='1.3.12.2.1107.5.2.6.24119.30000013121716094326500000390')
    ]
])