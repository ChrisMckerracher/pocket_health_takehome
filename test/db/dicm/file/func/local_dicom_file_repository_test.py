import glob
import os
import unittest

from fastapi import UploadFile

from src.db.dicom.file.repository.dicom_file_repository import InvalidDicomFileError
from src.db.dicom.file.repository.local_dicom_file_repository import LocalDicomFileRepository


class LocalDicomFileRepositoryTest(unittest.IsolatedAsyncioTestCase):

    def setUp(self) -> None:
        self.path = "/tmp"

        self.valid_file_path = "../../../../../assets/IM000001.dcm"
        self.file_size = 586394
        self.id = 1

        self.sut = LocalDicomFileRepository(path=self.path)

    def tearDown(self) -> None:
        map(os.remove, glob.glob(f"{self.path}/*.dcm"))

    async def test_save_and_get(self):
        content_type = "application/dicom"

        file = open(self.valid_file_path, "rb")
        upload_file = UploadFile(file=file, size=self.file_size, headers={
            "content-type": content_type
        })
        # content_type isn't in the init
        await self.sut.save(id=self.id, file=upload_file)
        self.compare_bytes(self.sut.get(self.id), self.valid_file_path)

    async def test_save_fails_with_incorrect_file_type(self):
        content_type = "application/invalid"

        file = open(self.valid_file_path, "rb")
        upload_file = UploadFile(file=file, size=self.file_size, headers={
            "content-type": content_type
        })

        with self.assertRaises(InvalidDicomFileError):
            await self.sut.save(id=self.id, file=upload_file)

    async def test_save_fails_when_no_file_size_defined(self):
        content_type = "application/dicom"

        file = open(self.valid_file_path, "rb")
        upload_file = UploadFile(file=file, headers={
            "content-type": content_type
        })

        with self.assertRaises(InvalidDicomFileError):
            await self.sut.save(id=self.id, file=upload_file)

    def compare_bytes(self, uploaded_file_path: str, original_file_path):
        expected = open(original_file_path, "rb")
        actual = open(uploaded_file_path, "rb")

        self.assertEquals(expected.read(), actual.read())


if __name__ == '__main__':
    unittest.main()
