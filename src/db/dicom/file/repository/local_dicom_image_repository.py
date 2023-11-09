from PIL import Image

from src.db.dicom.file.repository.dicom_image_repository import DicomImageRepository


class LocalDicomImageRepository(DicomImageRepository):
    path: str = "/tmp"
    img_type: str = ".png"

    def __init__(self, path: str = "/tmp", img_type: str = ".png"):
        self.path = path
        self.img_type = img_type

    async def _save(self, dcm_id: str, img: Image):
        path = f"{self.path}/{dcm_id}{self.img_type}"
        img.save(path)
        return path
