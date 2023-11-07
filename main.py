from typing import Any, Tuple

from fastapi import UploadFile

from src.server import app
from fastapi.responses import StreamingResponse


@app.get("/")
async def main():
    def iterfile():  #
        with open("png", mode="rb") as file_like:  #
            yield from file_like  #

    return StreamingResponse(iterfile(), media_type="image/png")


@app.post("/dicom")
async def post_file(file: UploadFile) -> int:
    pass

@app.put("/dicom")
async def put_file(dicom_id: int, file: UploadFile):
    pass


@app.post("/dicom/{dicom_id}/tag/{header_tag}")
async def query_header(dicom_id: int, header_tag: Tuple[int, int]) -> Any:
    pass


@app.get("/dicom/{dicom_id}?format={format}")
async def get(dicom_id: int, format=Any) -> Any:
    pass
