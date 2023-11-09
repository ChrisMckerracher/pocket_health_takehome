import uuid
from typing import Annotated

import uvicorn
from fastapi import UploadFile, Header
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel
from pydicom import dcmread

from src.db.dicom.dicom import Base
from src.db.session import ctx_session, SessionFactory
from src.domain.dicom.file.dicom_format import DicomFormat
from src.domain.dicom.img.image_converter import ImageConverter
from src.domain.dicom.tag.dicom_tag import DicomTag
from src.server import app
from src.server.ExceptionResponseMapper import map_exception
from src.server.env import create_dev_environment, Environment
from src.server.security import encode_token, assert_permission

environment: Environment = create_dev_environment()
# Normally I would do this in a cli, but this is 'functionally' a no-op if the tables are already created, with the
# caveat that doing a table orm update requires deleting the sqlite file and restarting server
Base.metadata.create_all(environment.engine)
ctx_session.set(SessionFactory(environment.engine))


class Message(BaseModel):
    message: str


@app.post("/patient/{patient_id}/dicom", responses={404: {"model": Message}, 401: {"model": Message}})
async def post_file(patient_id: str, body: UploadFile, access_token: Annotated[str | None, Header()] = None) -> str:
    """
    Upload a dicom file
    :param patient_id: the patient id
    :param body: the upload file
    :param access_token: Access token associated with the user
    :return: The uuid id of the uploaded file
    """
    # ToDo: sha hash of existing file with this to ensure no redundancy
    try:
        assert_permission(access_token, patient_id)

        # sha the file
        id = str(uuid.uuid4())

        await environment.dicom_file_repository.save(patient_id, body.filename, id, body)
        await body.seek(0)

        # ToDo: test that the pixel dataset isnt read
        dcm = dcmread(fp=body.file, stop_before_pixels=True)

        for key in dcm.keys():
            item = dcm.get(key)
            dcm_tag = DicomTag.from_data_element(item)
            await environment.dicom_tag_repository.save(dcm_id=id, tag=dcm_tag)

        return id
    except Exception as e:
        return map_exception(e)


@app.get("/patient/{patient_id}/dicom/{dicom_id}/tag/{header_tag}",
         responses={404: {"model": Message}, 401: {"model": Message}})
async def query_header(patient_id: str, dicom_id: str, header_tag: str,
                       access_token: Annotated[str | None, Header()] = None) -> DicomTag:
    """
    Query a header
    :param patient_id: the patient id
    :param dicom_id: the uuid associated with the dicom file
    :param header_tag: The groupId+element_id of the tag. Ex: 00081140 would map to 0008,1140
    :param access_token: Access token associated with the user
    :return: A simplified Dicom Tag
    """
    try:
        assert_permission(access_token, patient_id)

        # ToDo: Better exception
        if len(header_tag) != 8:
            raise Exception()
        group_id = int(header_tag[:4], 16)
        element_id = int(header_tag[4:], 16)
        return await environment.dicom_tag_repository.get(group_id, element_id, dicom_id)
    except Exception as e:
        return map_exception(e)


@app.get("/patient/{patient_id}/dicom/{dicom_id}",
         responses={404: {"model": Message}, 401: {"model": Message}, 422: {"model": Message}})
async def get(patient_id: str, dicom_id: str, content_type: Annotated[DicomFormat | None, Header()] = None,
              access_token: Annotated[str | None, Header()] = None) -> StreamingResponse:
    """
    Get a file associated with the dicom
    :param patient_id: the patient id
    :param dicom_id: the uuid associated with the dicom file
    :param content_type: Either application/dicom, or image/png are curently supported
    :param access_token: Access token associated with the user
    :return: A file relevant to the provided content type
    """
    try:
        assert_permission(access_token, patient_id)

        file_path: str = await environment.dicom_file_repository.get(dicom_id)

        def generator(file):
            yield from file

        match content_type:
            case DicomFormat.DCM:
                return StreamingResponse(generator(open(file_path, "rb")), media_type=DicomFormat.DCM.value)
            case DicomFormat.PNG:
                try:
                    img_file_path = await environment.dicom_img_repository.get(dicom_id)
                except FileNotFoundError:
                    file = dcmread(file_path)
                    image = ImageConverter.convert(file.pixel_array)
                    img_file_path = await environment.dicom_img_repository.save(dicom_id, image)
                return StreamingResponse(generator(open(img_file_path, "rb")), media_type=DicomFormat.PNG.value)
    except Exception as e:
        return map_exception(e)

    return JSONResponse(422, content={
        "message": "Invalid content-type"
    })


@app.get("/patient/{patient_id}/token")
async def get_token(patient_id: str):
    """
    A dev-only endpoint for generating user jwts in order to make queries
    :param patient_id: The id of the patient
    :return: A basic response with an Access-Token cookie
    """

    token = encode_token(patient_id)
    response = JSONResponse(content={
        "message": "Use this wisely!"
    })
    response.set_cookie(key="Access-Token", value=token)
    return response


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

# things i havent done: encrypted data/file, verify jwt(currently for the sake of the takehome, im just treating jwts as trusted without verifying). in prod we should be operating on zero trust, especially for something like patient records
