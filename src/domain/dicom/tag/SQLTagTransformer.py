from operator import attrgetter
from typing import List, ForwardRef, Optional

from src.db.dicom.dicom import DataSetItem
from src.domain.dicom.tag.dicom_tag import DicomTag

from itertools import groupby


class DataSetTree:
    id: str
    children: Optional[List[ForwardRef("DataSetTree")]] = None

def transform(dataset_items: List[DataSetItem]) -> DicomTag:
    for item in groupby(dataset_items, key=attrgetter("data_set_id")):
        pass
    return None


