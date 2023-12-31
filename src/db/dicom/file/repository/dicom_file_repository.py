from typing import Optional

from fastapi import UploadFile

from src.db.dicom.dicom import Dicom
from src.db.session import ctx_session

VALID_MIME_TYPE = "application/dicom"


class InvalidDicomFileError(Exception):
    pass


class DicomFileRepository:
    file_table = Dicom

    async def get(self, dicom_id: str) -> str:
        """
        :return: A file path 'openable' by python utils
        :raises FileNotFoundError if the file doesn't exist
        """
        session = ctx_session.get()
        dicom: Optional[Dicom] = session.get(Dicom, {
            "id": dicom_id
        })

        if not dicom:
            raise FileNotFoundError()

        return dicom.file_path

    async def save(self, patient_id: str, name: str, dicom_id: str, file: UploadFile) -> str:
        """
        Saves a file and returns the new file_path
        :return: the new file path
        """
        mime_type = file.content_type

        if mime_type != VALID_MIME_TYPE:
            raise InvalidDicomFileError()

        file_path = await self._save(dicom_id, file)
        session = ctx_session.get()
        session.add(Dicom(id=dicom_id, name=name, patient_id=patient_id, file_path=file_path))
        session.commit()

        return file_path

    async def _save(self, id: str, file: UploadFile) -> str:
        raise NotImplementedError("Failed to implement the interface for method save")
