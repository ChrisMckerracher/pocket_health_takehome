from src.domain.dicom.file.dicom_format import DicomFormat


class DicomFileConverter:

    @staticmethod
    def convert(file_path: str, format: DicomFormat):
        raise NotImplementedError()
