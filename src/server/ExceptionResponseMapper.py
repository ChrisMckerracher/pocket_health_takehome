from fastapi.responses import JSONResponse

from src.db.error.entity_not_found_error import EntityNotFoundError
from src.server.security import AccessViolationException


def map_exception(e: Exception):
    """
    Maps exceptions to a relevant HTTPResponse
    """
    e_type = type(e)
    if e_type is FileNotFoundError:
        return JSONResponse(status_code=404, content={
            "message": "File not found for entity"})
    elif e_type is EntityNotFoundError:
        return JSONResponse(status_code=404, content={
            "message": "File not found for entity"})
    elif e_type is AccessViolationException:
        return JSONResponse(status_code=401, content={
            "message": "Invalid access token for this patient"
        })
    else:
        return JSONResponse(status_code=500, content={
            "message": "An unmapped server error has occured. Please notify an admin."
        })

