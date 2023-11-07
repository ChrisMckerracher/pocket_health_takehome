from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel


class TagMap(Enum):
    pass
    # "00010002" = (vr,name)


class DicomTag(BaseModel):
    # id = Tup[number as str,number as str].toString sorta. Ex: (0001,0002) => "00010002"
    id: str
    format: Optional[str] = None
    name: Optional[str] = None
    value: Any
