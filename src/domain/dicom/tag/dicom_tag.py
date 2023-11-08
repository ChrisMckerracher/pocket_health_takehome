from enum import Enum
from typing import Union, List, ForwardRef, Generic, TypeVar

from deepdiff import DeepDiff
from pydantic import BaseModel

DataSet = List[ForwardRef("DicomTag")]
partial_T = Union[str, int, float, bytes]
T = TypeVar("T", bound=Union[partial_T, List[partial_T], List[DataSet]])


class TagMap(Enum):
    pass
    # "00010002" = (vr,name)


class DicomTag(BaseModel, Generic[T]):
    group_id: int
    element_id: int
    vr: str
    vm: int = 1
    name: str
    value: T

    def __eq__(self, other: ForwardRef("DicomTag")):
        return DeepDiff(self.model_dump(), other.model_dump(), ignore_order=True).tree == {}
