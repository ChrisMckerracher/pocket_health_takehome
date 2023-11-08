import os.path
from tempfile import SpooledTemporaryFile
from typing import Any, Optional

from fastapi import UploadFile

from src.db.dicom.file.dicom_file_repository import DicomFileRepository, InvalidDicomFileError

BLOCK_SIZE = 1024


class LocalDicomFileRepository(DicomFileRepository):
    path: str = "/tmp"

    def __init__(self, path: str = "/tmp"):
        self.path = path

    def get(self, id: str) -> str:
        path = f"{self.path}/{id}.dcm"

        if os.path.exists(path):
            return path
        else:
            raise FileNotFoundError()

    async def _save(self, id: str, file: UploadFile) -> SpooledTemporaryFile:
        tmp_file: SpooledTemporaryFile = file.file
        remaining_bytes: Optional[int] = file.size

        if not remaining_bytes:
            raise InvalidDicomFileError()

        remaining_bytes: int = remaining_bytes

        with open(f"{self.path}/{id}.dcm", "wb") as save_file:
            while remaining_bytes > 0:
                block = await file.read(size=min(BLOCK_SIZE, remaining_bytes))
                save_file.write(block)
                remaining_bytes -= BLOCK_SIZE

        return tmp_file
