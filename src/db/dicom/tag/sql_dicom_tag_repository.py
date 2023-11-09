import json
from typing import Optional, List, get_args
from uuid import uuid4, UUID

from src.db.dicom.dicom import DataSetItem, Tag, TagLookup
from src.db.dicom.tag.dicom_tag_repository import DicomTagRepository
from src.db.error.entity_not_found_error import EntityNotFoundError
from src.db.session import ctx_session
from src.domain.dicom.tag.sql_tag_transformer import transform
from src.domain.dicom.tag.dicom_tag import DicomTag, literals_T


#transaction

class SqlDicomTagRepository(DicomTagRepository):
    # ToDo: try catch and exception handling

    async def get(self, group_id: int, element_id: int, dcm_id: str) -> DicomTag:
        properties = {
            "group_id": group_id,
            "element_id": element_id,
            "dicom_id": dcm_id
        }
        scoped_session = ctx_session.get()

        # ToDo: n+1 query
        sql_dicom_tag: Optional[Tag] = scoped_session.query(Tag).get(properties)

        if not sql_dicom_tag:
            raise EntityNotFoundError(properties=properties)

        items: List[DataSetItem] = scoped_session.query(DataSetItem).filter(
            DataSetItem.tag_id == sql_dicom_tag.id).all()
        return transform(items)

    async def save(self, dcm_id: str, tag: DicomTag):
        # What should we do if you cant save?
        scoped_session = ctx_session.get()

        id = uuid4().__str__()
        tag_id = uuid4().__str__()
        self.add_tag_data(scoped_session, tag.group_id, tag.element_id, tag.vr, tag.name)
        scoped_session.add(Tag(id=tag_id, group_id=tag.group_id, element_id=tag.element_id, dicom_id=dcm_id))
        sql_dicom_tag = DataSetItem(id=id, group_id=tag.group_id, element_id=tag.element_id, tag_id=tag_id,
                                    data_set_id=None, parent_id=None, vm=tag.vm, sq=1)

        if tag.vr == "SQ":
            datasets: List[List[DicomTag]] = tag.value
            self.add_recursive_datasets(scoped_session, datasets, tag_id, id)
        else:
            sql_dicom_tag.value = tag.value if isinstance(tag.value, get_args(literals_T)) else json.dumps(tag.value)
        scoped_session.add(sql_dicom_tag)
        scoped_session.commit()
        return

    def add_recursive_datasets(self, scoped_session, datasets: List[List[DicomTag]], tag_id: str, parent_id: str):

        for dataset in datasets:
            dataset_id = uuid4().__str__()
            for tag in dataset:
                id = uuid4().__str__()
                sql_dicom_tag = DataSetItem(id=id, parent_id=parent_id, group_id=tag.group_id,
                                            element_id=tag.element_id,
                                            tag_id=tag_id,
                                            data_set_id=dataset_id, vm=tag.vm)

                if tag.vr == "SQ":
                    datasets: List[List[DicomTag]] = tag.value
                    self.add_recursive_datasets(scoped_session, datasets, tag_id, id)
                else:
                    sql_dicom_tag.value = tag.value if isinstance(tag.value, get_args(literals_T)) else json.dumps(tag.value)

                self.add_tag_data(scoped_session, tag.group_id, tag.element_id, tag.vr, tag.name)
                scoped_session.add(sql_dicom_tag)

    def add_tag_data(self, scoped_session, group_id, element_id, vr, name):
        if not scoped_session.query(TagLookup).get({
            "group_id": group_id,
            "element_id": element_id
        }):
            scoped_session.add(
                TagLookup(group_id=group_id, element_id=element_id, vr=vr, name=name))
