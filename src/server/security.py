import jwt

public_key = "dev_key_for_testing"
algo = "HS256"


def encode_token(patient_id: str) -> str:
    """
    Create a dev jwt token
    """
    return jwt.encode({
        "patient_id": patient_id
    }, public_key, algorithm=algo)


class AccessViolationException(Exception):
    pass


def assert_permission(access_token, patient_id: str):
    """
    Assert that the access_token pertains to the patient_id
    :raises AccessViolationException if the access_token doesn't pertain to the patient_id
    """
    try:
        access_token = jwt.decode(access_token, public_key, algorithms=algo)
    except Exception as e:
        raise AccessViolationException()
    if access_token["patient_id"] != patient_id:
        raise AccessViolationException()
