from typing import Any, Tuple

from src.server import app
from fastapi.responses import StreamingResponse



@app.post("/dicom")
async def post_file(a : Any) -> int:
    pass

@app.post("/dicom/{dicom_id}/tag/{header_tag}")
async def query_header(dicom_id: int, header_tag: Tuple[int, int]) -> Any:
    pass

@app.get("/dicom/{dicom_id}?format={format}")
async def get(dicom_id: int, format=Any) -> Any:
    pass
