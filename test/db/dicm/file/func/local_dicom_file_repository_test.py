import glob
import os
import unittest

from fastapi import UploadFile
from sqlalchemy import create_engine

from assets import ASSET_DIR
from src.db.dicom.dicom import Base
from src.db.dicom.file.repository.dicom_file_repository import InvalidDicomFileError
from src.db.dicom.file.repository.local_dicom_file_repository import LocalDicomFileRepository
from src.db.session import ctx_session, SessionFactory


class LocalDicomFileRepositoryTest(unittest.IsolatedAsyncioTestCase):
    tmp_sqlite_file = "/tmp/sql_app.db"

    async def asyncSetUp(self) -> None:
        self.path = "/tmp"

        self.valid_file_path = f"{ASSET_DIR}/IM000001.dcm"
        self.file_size = 586394
        self.id = "dcm_id"
        self.patient_id = "patient_id"

        engine = create_engine(f"sqlite:///{self.tmp_sqlite_file}")
        Base.metadata.create_all(engine)
        ctx_session.set(SessionFactory(engine))

        self.sut = LocalDicomFileRepository(path=self.path)

    async def asyncTearDown(self) -> None:
        os.remove(self.tmp_sqlite_file)

    def tearDown(self) -> None:
        map(os.remove, glob.glob(f"{self.path}/*.dcm"))

    async def test_save_and_get(self):
        content_type = "application/dicom"

        file = open(self.valid_file_path, "rb")
        upload_file = UploadFile(file=file, size=self.file_size, headers={
            "content-type": content_type
        })
        # content_type isn't in the init
        await self.sut.save(patient_id=self.patient_id, name="foo", dicom_id=self.id, file=upload_file)
        self.compare_bytes(await self.sut.get(self.id), self.valid_file_path)

    async def test_save_fails_with_incorrect_file_type(self):
        content_type = "application/invalid"

        file = open(self.valid_file_path, "rb")
        upload_file = UploadFile(file=file, size=self.file_size, headers={
            "content-type": content_type
        })

        with self.assertRaises(InvalidDicomFileError):
            await self.sut.save(patient_id=self.patient_id, name="foo", dicom_id=self.id, file=upload_file)

    async def test_save_fails_when_no_file_size_defined(self):
        content_type = "application/dicom"

        file = open(self.valid_file_path, "rb")
        upload_file = UploadFile(file=file, headers={
            "content-type": content_type
        })

        with self.assertRaises(InvalidDicomFileError):
            await self.sut.save(patient_id=self.patient_id, name="foo", dicom_id=self.id, file=upload_file)

    def compare_bytes(self, uploaded_file_path: str, original_file_path):
        expected = open(original_file_path, "rb")
        actual = open(uploaded_file_path, "rb")

        self.assertEquals(expected.read(), actual.read())


if __name__ == '__main__':
    unittest.main()
