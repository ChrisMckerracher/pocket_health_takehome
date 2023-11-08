from typing import Dict

from pydicom import FileDataset

from src.domain.dicom.tag.dicom_tag import DicomTag


class DicomTagExtractor:

    @staticmethod
    def extract(file_data: FileDataset) -> Dict[str, DicomTag]:
        raise NotImplementedError()