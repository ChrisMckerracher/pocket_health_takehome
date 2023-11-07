from src.domain.dicom.tag.dicom_tag import DicomTag


class DicomTagRepository:

    def get(self, tag_id: str, dcm_id: int) -> DicomTag:
        raise NotImplementedError()

    def save(self, dcm_id: str, tag: DicomTag):
        raise NotImplementedError()