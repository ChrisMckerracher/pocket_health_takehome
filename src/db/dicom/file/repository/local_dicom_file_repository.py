import os.path
from tempfile import SpooledTemporaryFile
from typing import Optional

from fastapi import UploadFile

from src.db.dicom.file.repository.dicom_file_repository import DicomFileRepository, InvalidDicomFileError

BLOCK_SIZE = 1024


class LocalDicomFileRepository(DicomFileRepository):
    path: str = "/tmp"

    def __init__(self, path: str = "/tmp"):
        self.path = path

    async def _save(self, dcm_id: str, file: UploadFile) -> str:
        path = f"{self.path}/{dcm_id}.dcm"
        tmp_file: SpooledTemporaryFile = file.file
        remaining_bytes: Optional[int] = file.size

        if not remaining_bytes:
            raise InvalidDicomFileError()

        remaining_bytes: int = remaining_bytes

        with open(path, "wb") as save_file:
            while remaining_bytes > 0:
                block = await file.read(size=min(BLOCK_SIZE, remaining_bytes))
                save_file.write(block)
                remaining_bytes -= BLOCK_SIZE

        return path
