from typing import Union, List, ForwardRef, Generic, TypeVar, get_args

from deepdiff import DeepDiff
from pydantic import BaseModel
from pydicom import DataElement, Dataset
from pydicom.multival import MultiValue

DataSet = List[ForwardRef("DicomTag")]
literals_T = Union[str, int, float, bytes]
bound_T = Union[literals_T, List[literals_T], List[DataSet]]
T = TypeVar("T", bound=bound_T)


class DicomTag(BaseModel, Generic[T]):
    group_id: int
    element_id: int
    vr: str
    vm: int = 1
    name: str
    value: T

    def __eq__(self, other: ForwardRef("DicomTag")):
        return DeepDiff(self.model_dump(), other.model_dump(), ignore_order=True).tree == {}

    @staticmethod
    def from_data_element(tag: DataElement) -> ForwardRef("DicomTag"):
        """

        :param tag: The pydicom dataelement
        :return: A tag entity representation of the dataelement
        """
        vr = tag.VR
        group_id = tag.tag.group
        element_id = tag.tag.element
        vm = tag.VM
        name = tag.name
        value: T

        if vr == "SQ":
            children: List[DataSet] = []
            for dataset in tag.value:
                child: DataSet = []
                dataset: Dataset
                for sub_tag in dataset:
                    child.append(DicomTag.from_data_element(sub_tag))
                children.append(child)
            value = children
        else:
            # stuff like PersonName isnt any of the valid types, therefore we just want to simplify the representation
            val_type = type(tag.value)
            # you cant check is_instance against generic types like List. We assuime the list data is well formed, as we assume pydicom gave us a well formed value
            if val_type is list or val_type is MultiValue and len(tag.value):
                value = [x if isinstance(x, get_args(literals_T)) else str(x) for x in tag.value]
            else:
                value = tag.value if isinstance(val_type, get_args(literals_T)) else str(tag.value)

        return DicomTag(group_id=group_id, element_id=element_id, vr=vr, vm=vm, name=name, value=value)
