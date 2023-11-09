from typing import Annotated

import jwt
import uvicorn
from fastapi import UploadFile, HTTPException, Header

from src.db.dicom.dicom import Base
from src.db.session import ctx_session, SessionFactory
from src.domain.dicom.file.dicom_format import DicomFormat
from src.domain.dicom.img.image_converter import ImageConverter
from src.domain.dicom.tag.dicom_tag import DicomTag
from src.server import app
import uuid
from pydicom import dcmread
from fastapi.responses import StreamingResponse, JSONResponse

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


@app.post("/patient/{patient_id}/dicom")
async def post_file(patient_id: str, body: UploadFile, access_token: Annotated[str | None, Header()] = None) -> str:
    assert_permission(access_token, patient_id)

    # sha the file
    id = uuid.uuid4().__str__()

    await environment.dicom_file_repository.save(patient_id, body.filename, id, body)
    await body.seek(0)

    # ToDo: test that the pixel dataset isnt read
    dcm = dcmread(fp=body.file, stop_before_pixels=True)

    for key in dcm.keys():
        item = dcm.get(key)
        dcm_tag = DicomTag.from_data_element(item)
        await environment.dicom_tag_repository.save(dcm_id=id, tag=dcm_tag)

    return id


@app.get("/patient/{patient_id}/dicom/{dicom_id}/tag/{header_tag}")
async def query_header(patient_id: str, dicom_id: str, header_tag: str,
                       access_token: Annotated[str | None, Header()] = None) -> DicomTag:
    assert_permission(access_token, patient_id)

    # ToDo: Better exception
    if len(header_tag) != 8:
        raise Exception()
    group_id = int(header_tag[:4], 16)
    element_id = int(header_tag[4:], 16)
    return await environment.dicom_tag_repository.get(group_id, element_id, dicom_id)


@app.get("/patient/{patient_id}/dicom/{dicom_id}")
async def get(patient_id: str, dicom_id: str, content_type: Annotated[DicomFormat | None, Header()] = None,
              access_token: Annotated[str | None, Header()] = None) -> StreamingResponse:
    assert_permission(access_token, patient_id)
    file_path: str

    def generator(file):
        yield from file

    match content_type:
        case DicomFormat.DCM:
            file_path = await environment.dicom_file_repository.get(dicom_id)

            return StreamingResponse(generator(open(file_path, "rb")), media_type=DicomFormat.DCM.value)
        case DicomFormat.PNG:
            try:
                file_path = await environment.dicom_img_repository.get(dicom_id)
            except FileNotFoundError:
                file_path = await environment.dicom_file_repository.get(dicom_id)
                file = dcmread(file_path)
                image = ImageConverter.convert(file.pixel_array)
                file_path = await environment.dicom_img_repository.save(dicom_id, image)
            return StreamingResponse(generator(open(file_path, "rb")), media_type=DicomFormat.PNG.value)

    return None


public_key = "dev_key_for_testing"
algo = "HS256"


@app.get("/patient/{patient_id}/token")
async def get_token(patient_id: str):
    """
    A dev-only endpoint for generating user jwts in order to make queries
    :param patient_id:
    :return:
    """

    token = jwt.encode({
        "patient_id": patient_id
    }, public_key, algorithm=algo)

    response = JSONResponse(content={
        "message": "Use this wisely!"
    })
    response.set_cookie(key="Access-Token", value=token)
    return response


def assert_permission(access_token, patient_id: str):
    access_token = jwt.decode(access_token, public_key, algorithms=algo)
    if access_token["patient_id"] != patient_id:
        raise HTTPException(401, "Invalid access string")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

# things i havent done: encrypted data/file, verify jwt(currently for the sake of the takehome, im just treating jwts as trusted without verifying). in prod we should be operating on zero trust, especially for something like patient records
