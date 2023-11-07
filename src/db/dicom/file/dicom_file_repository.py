from tempfile import SpooledTemporaryFile
from typing import Any

from fastapi import UploadFile

VALID_MIME_TYPE = "application/dicom"

class InvalidDicomFileError(Exception):
    pass

class DicomFileRepository:
    async def get(self, id: int) -> str:
        raise NotImplementedError("Failed to implement the interface for method get")

    async def save(self, id: int, file: UploadFile) -> SpooledTemporaryFile:
        mime_type = file.content_type

        if mime_type != VALID_MIME_TYPE:
            raise InvalidDicomFileError()


        return await self._save(id, file)

    async def _save(self, id: int, file: UploadFile) -> SpooledTemporaryFile:
        raise NotImplementedError("Failed to implement the interface for method save")
