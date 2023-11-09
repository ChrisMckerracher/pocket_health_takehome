from src.domain.dicom.tag.dicom_tag import DicomTag


class DicomTagRepository:

    async def get(self, group_id: int, element_id: int, dcm_id: str) -> DicomTag:
        """
        :return: A tag relevant to the params
        :raises EntityNotFoundError if the entity doesn't exist
        """
        raise NotImplementedError()

    async def save(self, dcm_id: str, tag: DicomTag):
        """
        Saves a relevant tag
        """
        raise NotImplementedError()
