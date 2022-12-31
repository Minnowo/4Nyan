from fastapi import HTTPException, status


API_400_BAD_REQUEST_EXCEPTION = HTTPException(
    status_code=400,
    detail="bad request",
)

API_400_BAD_FILE_EXCEPTION = HTTPException(
    status_code=400,
    detail="unsupported file",
)


API_401_CREDENTIALS_EXCEPTION = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


API_404_NOT_FOUND_EXCEPTION = HTTPException(
    status_code=404,
    detail="not found",
)

API_404_USER_NOT_FOUND_EXCEPTION = HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="user does not exist")


API_409_FILE_EXISTS_EXCEPTION = HTTPException(
    status_code=409,
    detail="File already exists",
)

API_409_TAG_CREATION_EXCEPTION = HTTPException(
    status_code=409,
    detail="Tag conflict, it may already exist",
)

API_409_USERNAME_CONFLICT_EXCEPTION = HTTPException(status_code=status.HTTP_409_CONFLICT, detail="username already exists")

API_406_USERNAME_EXCEPTION = HTTPException(
    status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="username does not follow guidelines"
)

API_406_PASSWORD_EXCEPTION = HTTPException(
    status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="password does not follow guidelines"
)


API_500_SIGNATURE_EXCEPTION = HTTPException(
    status_code=500,
    detail="server error",
)

API_500_OSERROR = HTTPException(
    status_code=500,
    detail="server error",
)

API_500_NOT_IMPLEMENTED = HTTPException(
    status_code=500,
    detail="Not implemented",
)
