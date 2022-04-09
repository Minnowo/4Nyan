from fastapi import HTTPException, status

API_418_TEAPOT_EXCEPTION = HTTPException(
    status_code=418,
    detail="I'm a teapot",
)

API_400_BAD_REQUEST_EXCEPTION = HTTPException(
    status_code=400,
    detail="bad request",
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

API_409_EMAIL_CONFLICT_EXCEPTION = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="email already exists"
)

API_500_SIGNATURE_EXCEPTION = HTTPException(
    status_code=500,
    detail="server error",
)

API_406_INVALID_PURCHASE_QUANTITY = HTTPException(
    status_code=406,
    detail="invalid purchase quantity"
)

API_406_EMPTY_CART_EXCEPTION = HTTPException(
    status_code=406,
    detail="cart is empy"
)


API_404_USER_NOT_FOUND_EXCEPTION = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="user does not exist"
)

API_409_USERNAME_CONFLICT_EXCEPTION = HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="username already exists"
        )

API_406_USERNAME_EXCEPTION = HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="username does not follow guidelines"
        )

API_406_PASSWORD_EXCEPTION = HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="password does not follow guidelines"
        )
