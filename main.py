from typing import Any, Tuple

import uvicorn
from fastapi import UploadFile, Request
from pydicom.tag import BaseTag

from src.db.dicom.dicom import Base
from src.db.session import ctx_session, SessionFactory
from src.domain.dicom.tag.dicom_tag import DicomTag
from src.server import app
from fastapi.responses import StreamingResponse
import uuid
from pydicom import dcmread

from src.server.env import create_dev_environment, Environment

environment: Environment = create_dev_environment()
Base.metadata.create_all(environment.engine)
ctx_session.set(SessionFactory(environment.engine))


@app.get("/")
async def main():
    def iterfile():  #
        with open("png", mode="rb") as file_like:  #
            yield from file_like  #

    return StreamingResponse(iterfile(), media_type="image/png")


@app.post("/dicom")
async def post_file(body: UploadFile) -> int:
    #sha the file
    id = uuid.uuid4().int & (2 ** 32 - 1)

    await environment.dicom_file_repository.save(id, body)
    await body.seek(0)

    #ToDo: test that the pixel dataset isnt read
    dcm = dcmread(fp=body.file, stop_before_pixels=True)
    tag_ids = dcm.__dict__['_dict']

    for tag_id in tag_ids:
        tag_id: BaseTag
        tag = dcm.get(tag_id)
        str_val = tag.repval
        tag_id = "{0:04x}{1:04x}".format(tag_id.group, tag_id.element)
        dcm_tag = DicomTag(id=tag_id, value=str_val)
        await environment.dicom_tag_repository.save(dcm_id=id, tag=dcm_tag)

    return id


@app.put("/dicom")
async def put_file(dicom_id: int, file: UploadFile):
    pass


@app.get("/dicom/{dicom_id}/tag/{header_tag}")
async def query_header(dicom_id: int, header_tag: str) -> DicomTag:
    return await environment.dicom_tag_repository.get(header_tag, dicom_id)


@app.get("/dicom/{dicom_id}?format={format}")
async def get(dicom_id: int, format=Any) -> Any:
    pass


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

# things i havent done: encrypted data/file, verify jwt(currently for the sake of the takehome, im just treating jwts as trusted without verifying). in prod we should be operating on zero trust, especially for something like patient records
