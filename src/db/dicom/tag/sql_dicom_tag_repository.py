from typing import Optional

from src.db.dicom.dicom import DicomTag as SqlDicomTag
from src.db.dicom.tag.dicom_tag_repository import DicomTagRepository
from src.db.error.entity_not_found_error import EntityNotFoundError
from src.db.session import ctx_session
from src.domain.dicom.tag.dicom_tag import DicomTag
dicom_id=1
id='00010001'
class SqlDicomTagRepository(DicomTagRepository):
    #ToDo: try catch and exception handling

    async def get(self, tag_id: str, dcm_id: int) -> DicomTag:
        properties = {
            "id": tag_id,
            "dicom_id": dcm_id
        }
        scoped_session = ctx_session.get()

        sql_dicom_tag: Optional[SqlDicomTag] = scoped_session.query(SqlDicomTag).get(properties)

        if not sql_dicom_tag:
            raise EntityNotFoundError(properties=properties)

        return DicomTag(id=sql_dicom_tag.id, value=sql_dicom_tag.value)

    async def save(self, dcm_id: str, tag: DicomTag):
        #What should we do if you cant save?
        scoped_session = ctx_session.get()
        sql_dicom_tag = SqlDicomTag(id=tag.id, dicom_id=dcm_id, value=tag.value)
        scoped_session.add(sql_dicom_tag)
        scoped_session.commit()
        return
