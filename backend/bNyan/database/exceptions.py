



from fastapi import HTTPException

API_500_FILE_EXISTS_EXCEPTION = HTTPException(
    status_code=500,
    detail="File already exists",
)









