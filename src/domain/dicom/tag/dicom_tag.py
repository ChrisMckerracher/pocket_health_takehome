from enum import Enum
from typing import Any

from pydantic import BaseModel

class TagMap(Enum):
     "00010002" = (vr,name)

class DicomTag(BaseModel):
    # id = Tupe[int,int].toString sorta. Ex: (0001,0002) => "00010002"
    id : str
    format: str
    name: str
    value: Any
