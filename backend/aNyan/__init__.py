import logging

from .api import APIConstants, APIRouting, APIFastAPI

from .core import aNyanLogging


def main():

    import uvicorn

    aNyanLogging.setup_logger("./logs.log")

    app = APIFastAPI.Nyan_API()
    app.include_router(APIRouting.Search_Routing())
    app.include_router(APIRouting.Static_Routing())

    try:
        uvicorn.run(app, host=APIConstants.SERVER_IP, port=APIConstants.SERVER_PORT)

    except Exception as e:
        logging.critical(e.__repr__(), stack_info=True)
