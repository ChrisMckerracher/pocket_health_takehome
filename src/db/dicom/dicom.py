from sqlalchemy import Column, ARRAY, Integer, String, ForeignKey, Uuid, PrimaryKeyConstraint, ForeignKeyConstraint, \
    UniqueConstraint, LargeBinary
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


# storing this in a sql table for persistent knowledge of file location. Atm theres a direct mapping of id = filename, but thats not necessarily soemthing that will hold
class Dicom(Base):
    __tablename__ = 'dicom'
    # sqlite doesnt support uuid in sqlalchemy apparently

    id = Column(String, primary_key=True)
    patient_id = Column(String)  # Column(ForeignKey("patient.id"))
    name = Column(String)
    file_path = Column(String)
    # ToDo: implement cascading delete


class ImageData(Base):
    __tablename__ = 'imagedata'

    dicom_id = Column(ForeignKey("dicom.id"))
    file_path = Column(String)

    __table_args__ = (
        PrimaryKeyConstraint('dicom_id'),
    )


class Tag(Base):
    __tablename__ = 'tag'

    id = Column(String, unique=True)
    group_id = Column(Integer)
    element_id = Column(Integer)
    dicom_id = Column(Integer)

    __table_args__ = (
        PrimaryKeyConstraint('group_id', 'element_id', 'dicom_id'),
    )


class DataSetItem(Base):
    __tablename__ = 'data'

    id = Column(String, primary_key=True)

    group_id = Column(Integer)
    element_id = Column(Integer)

    tag_id = Column(ForeignKey("tag.id"))
    # 1 2 or 3...
    data_set_id = Column(String)
    parent_id = Column(ForeignKey("data.id"))
    # 1 2 or 3...
    sq = Column(Integer)
    vm = Column(Integer)

    # sqllite doesnt support array
    value = Column(String)

    __table_args__ = (
        ForeignKeyConstraint(['group_id', 'element_id'], ['taglookup.group_id', 'taglookup.element_id']),
    )

    tag_lookup = relationship("TagLookup",
                              primaryjoin="and_(DataSetItem.group_id == TagLookup.group_id, DataSetItem.element_id == TagLookup.element_id)")


class TagLookup(Base):
    __tablename__ = "taglookup"
    group_id = Column(Integer)
    element_id = Column(Integer)
    vr = Column(String)
    name = Column(String)

    __table_args__ = (
        PrimaryKeyConstraint('group_id', 'element_id'),
    )
