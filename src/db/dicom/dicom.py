from sqlalchemy import Column, Integer, String, ForeignKey, PrimaryKeyConstraint
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Dicom(Base):
    id = Column(Integer, primary_key=True)
    name = Column(String)
    file_path = Column(String)

class DicomTag(Base):
    #Format and name are fixed depending on id, as such we don't need to store more than this
    id = Column(Integer)
    dicom_id = Column(ForeignKey("dicom.id"))
    value = Column(String)

    __table_args__ = (
        PrimaryKeyConstraint(id, dicom_id),
        {},
    )


