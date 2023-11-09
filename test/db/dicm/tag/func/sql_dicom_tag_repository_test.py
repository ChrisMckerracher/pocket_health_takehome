import os
import unittest
from typing import List

from sqlalchemy import create_engine
from src.db.dicom.dicom import Base
from src.db.dicom.tag.sql_dicom_tag_repository import SqlDicomTagRepository
from src.db.error.entity_not_found_error import EntityNotFoundError
from src.domain.dicom.tag.dicom_tag import DicomTag, DataSet
from src.db.session import ctx_session, SessionFactory


class LocalDicomFileRepositoryTest(unittest.IsolatedAsyncioTestCase):
    tmp_sqlite_file = "/tmp/sql_app.db"

    class Helper:
        @staticmethod
        async def test_save_and_get(self, expected: DicomTag):
            dcm_tag = 1
            await self.sut.save(dcm_tag, expected)

            actual = await self.sut.get(expected.group_id, expected.element_id, dcm_tag)

            self.assertEquals(expected, actual)

    def setUp(self) -> None:
        engine = create_engine(f"sqlite:///{self.tmp_sqlite_file}")
        Base.metadata.create_all(engine)
        ctx_session.set(SessionFactory(engine))
        self.sut = SqlDicomTagRepository()

    def tearDown(self) -> None:
        os.remove(self.tmp_sqlite_file)

    async def test_basic_save_and_get(self):
        await LocalDicomFileRepositoryTest.Helper.test_save_and_get(self, self.create_basic_tag())

    async def test_complex_save_and_get(self):
        await LocalDicomFileRepositoryTest.Helper.test_save_and_get(self, self.create_complex_tag())

    async def test_save_and_get_list_non_sq(self):
        await LocalDicomFileRepositoryTest.Helper.test_save_and_get(self, self.create_list_tag())

    async def test_get_invalid_key(self):
        dcm_tag = 1000
        expected_group_id = 1
        expected_element_id = 1

        with self.assertRaises(EntityNotFoundError):
            await self.sut.get(expected_group_id, expected_element_id, dcm_tag)

    @staticmethod
    def create_basic_tag() -> DicomTag[str]:
        return DicomTag[str](group_id=8, element_id=4432,
                             name="Referenced SOP Class UID", vr="UI",
                             value='1')

    @staticmethod
    def create_list_tag() -> DicomTag[List[int]]:
        return DicomTag[List[int]](group_id=8, element_id=4416, name="Referenced Image Sequence", vr="SL", vm=4,
                                   value=[1, 3, 5, 7])

    @staticmethod
    def create_complex_tag() -> DicomTag[List[DataSet]]:
        return DicomTag[List[DataSet]](group_id=8, element_id=4416, name="Referenced Image Sequence", vr="SQ",
                                       value=[
                                           [
                                               DicomTag[str](group_id=8, element_id=4432,
                                                             name="Referenced SOP Class UID", vr="UI",
                                                             value='1.2.840.10008.5.1.4.1.1.4'),
                                               DicomTag[str](group_id=8, element_id=4437,
                                                             name="Referenced SOP Instance UID", vr="UI",
                                                             value='1.3.12.2.1107.5.2.6.24119.30000013121716094326500000391')
                                           ],
                                           [
                                               DicomTag[str](group_id=8, element_id=4432,
                                                             name="Referenced SOP Class UID", vr="UI",
                                                             value='1.2.840.10008.5.1.4.1.1.4'),
                                               DicomTag[str](group_id=8, element_id=4437,
                                                             name="Referenced SOP Instance UID", vr="UI",
                                                             value='1.3.12.2.1107.5.2.6.24119.30000013121716094326500000392')
                                           ],
                                           [
                                               DicomTag[str](group_id=8, element_id=4432,
                                                             name="Referenced SOP Class UID", vr="UI",
                                                             value='1.2.840.10008.5.1.4.1.1.4'),
                                               DicomTag[List[int]](group_id=8, element_id=4410,
                                                                   name="Referenced Image Sequence", vr="SL", vm=4,
                                                                   value=[1, 3, 5, 7])
                                           ],
                                           [
                                               DicomTag[List[DataSet]](group_id=8, element_id=4416,
                                                                       name="Referenced Image Sequence",
                                                                       vr="SQ",
                                                                       value=[[
                                                                           DicomTag[str](group_id=8,
                                                                                         element_id=4432,
                                                                                         name="Referenced SOP Class UID",
                                                                                         vr="UI",
                                                                                         value='1.2.840.10008.5.1.4.1.1.4'),
                                                                           DicomTag[str](group_id=8,
                                                                                         element_id=4437,
                                                                                         name="Referenced SOP Instance UID",
                                                                                         vr="UI",
                                                                                         value='1.3.12.2.1107.5.2.6.24119.30000013121716094326500000391')
                                                                       ]]),
                                               DicomTag[List[DataSet]](group_id=8, element_id=4417,
                                                                       name="Referenced Image Sequence",
                                                                       vr="SQ",
                                                                       value=[[
                                                                           DicomTag[str](group_id=8,
                                                                                         element_id=4432,
                                                                                         name="Referenced SOP Class UID",
                                                                                         vr="UI",
                                                                                         value='1.2.840.10008.5.1.4.1.1.4'),
                                                                           DicomTag[str](group_id=8,
                                                                                         element_id=4437,
                                                                                         name="Referenced SOP Instance UID",
                                                                                         vr="UI",
                                                                                         value='1.3.12.2.1107.5.2.6.24119.30000013121716094326500000391')
                                                                       ]])
                                           ]
                                       ])


if __name__ == '__main__':
    unittest.main()
