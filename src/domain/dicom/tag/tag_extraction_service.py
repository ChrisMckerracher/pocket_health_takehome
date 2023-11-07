from typing import Dict

from pydicom import FileDataset

from src.db.dicom.dicom import DicomTag


class DicomTagExtractor:

    @staticmethod
    def extract(file_data: FileDataset) -> Dict[str, DicomTag]:
        raise NotImplementedError()