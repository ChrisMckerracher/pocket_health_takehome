import os
import unittest

from sqlalchemy import create_engine
from src.db.dicom.dicom import DicomTag as SqlDicomTag, Dicom as SqlDicom, Base
from src.db.dicom.tag.sql_dicom_tag_repository import SqlDicomTagRepository
from src.db.error.entity_not_found_error import EntityNotFoundError
from src.domain.dicom.tag.dicom_tag import DicomTag
from src.db.session import ctx_session, SessionFactory


class SqlDicomTagRepositoryTest(unittest.TestCase):

    tmp_sqlite_file = "/tmp/sql_app.db"

    def setUp(self) -> None:
        engine = create_engine(f"sqlite:///{self.tmp_sqlite_file}")
        Base.metadata.create_all(engine)
        ctx_session.set(SessionFactory(engine))
        self.sut = SqlDicomTagRepository()

    def tearDown(self) -> None:
        os.remove(self.tmp_sqlite_file)

    def test_save_and_get(self):
        dcm_tag = 1
        expected_id = "00010001"
        expected_value = "3"

        expected = DicomTag(id=expected_id, value=expected_value)
        self.sut.save(dcm_tag, expected)

        actual = self.sut.get(expected_id, dcm_tag)

        self.assertEquals(expected, actual)

    def test_get_invalid_key(self):
        dcm_tag = 1000
        expected_id = "00010001"


        with self.assertRaises(EntityNotFoundError):
            self.sut.get(expected_id, dcm_tag)





if __name__ == '__main__':
    unittest.main()
