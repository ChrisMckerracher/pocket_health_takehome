from dataclasses import dataclass

from sqlalchemy import Engine, create_engine

from src.constants.db import SQLALCHEMY_DATABASE_URL
from src.db.dicom.file.repository.dicom_file_repository import DicomFileRepository
from src.db.dicom.file.repository.dicom_image_repository import DicomImageRepository
from src.db.dicom.file.repository.local_dicom_file_repository import LocalDicomFileRepository
from src.db.dicom.file.repository.local_dicom_image_repository import LocalDicomImageRepository
from src.db.dicom.tag.dicom_tag_repository import DicomTagRepository
from src.db.dicom.tag.sql_dicom_tag_repository import SqlDicomTagRepository


# We don't really need to use BaseModel here over just dataclass, as this isn't so much a logical business entity
# It doesn't really matter, but I tend to associated BaseModel, pydanticy stuff as entities that require validation
@dataclass
class Environment:
    engine: Engine
    dicom_file_repository: DicomFileRepository
    dicom_tag_repository: DicomTagRepository
    dicom_img_repository: DicomImageRepository


def create_dev_environment() -> Environment:
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    dicom_file_repository = LocalDicomFileRepository()
    dicom_tag_repository = SqlDicomTagRepository()
    dicom_img_repository = LocalDicomImageRepository()

    return Environment(engine=engine, dicom_file_repository=dicom_file_repository, dicom_tag_repository=dicom_tag_repository, dicom_img_repository=dicom_img_repository)
