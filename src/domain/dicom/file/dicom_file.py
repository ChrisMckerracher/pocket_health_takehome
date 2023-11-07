from pydantic import BaseModel


class DicomFile(BaseModel):
    id: int
    file_path: str
