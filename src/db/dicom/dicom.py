from sqlalchemy import Column, Integer, String, ForeignKey, PrimaryKeyConstraint
from sqlalchemy.orm import declarative_base

Base = declarative_base()


# storing this in a sql table for persistent knowledge of file location. Atm theres a direct mapping of id = filename, but thats not necessarily soemthing that will hold
class Dicom(Base):
    __tablename__ = 'dicom'
    id = Column(Integer, primary_key=True)
    #Column(ForeignKey("patient.id"))
    patient_id = Column(String)
    name = Column(String)
    file_path = Column(String)

# Sql as theres little benefit to loading a file, or even portion of a dcm file, loading the entire file map into memory, or even just reading until the id is found
# would make every get request require more memory bandwidth than is needed
class DicomTag(Base):
    __tablename__ = 'tag'
    #Format and name are fixed depending on id, as such we don't need to store more than this
    id = Column(String)
    dicom_id = Column(ForeignKey("dicom.id"))
    value = Column(String)

    __table_args__ = (
        PrimaryKeyConstraint(id, dicom_id),
        {},
    )


