from typing import Optional

from fastapi import UploadFile

from src.db.dicom.dicom import ImageData
from src.db.session import ctx_session


class DicomImageRepository:
    img_table = ImageData

    async def get(self, dicom_id: str) -> str:
        """
        :return: A file path 'openable' by python utils
        :raises FileNotFoundError if the file doesn't exist
        """
        session = ctx_session.get()
        img: Optional[ImageData] = session.get(ImageData, {
            "dicom_id": dicom_id
        })

        if not img:
            raise FileNotFoundError()

        return img.file_path

    async def save(self, dicom_id: str, file: UploadFile) -> str:
        file_path = await self._save(dicom_id, file)

        session = ctx_session.get()
        session.add(ImageData(dicom_id=dicom_id, file_path=file_path))
        session.commit()

        return file_path

    async def _save(selfs, dicom_id: str, file: UploadFile) -> str:
        raise NotImplementedError()
