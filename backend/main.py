
import exceptions

from fastapi import FastAPI, Depends, status, Request, Response
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from fastapi import Header
from fastapi.responses import StreamingResponse

from methods import CATEGORY_MAP

app = FastAPI()

origins = [
    "http://localhost:3000",
    "localhost:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


@app.get('/')
async def get_item():
    return "hello world"

@app.get('/static/{category}/')
async def get_item1(category : str):
    return category 


@app.get('/static/{category}/{path}')
async def static(category: str, path: str, request : Request):
    
    cat = CATEGORY_MAP.get(category, None)

    if cat is None:
        raise exceptions.API_404_NOT_FOUND_EXCEPTION

    return cat(path, request)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=721)



# from flask import Flask

# app = Flask(__name__)

# @app.route("/")
# def hello_world():
#     return "<p>Hello, World!</p>"


# if __name__ == "__main__":
#     app.run(host="0.0.0.0", port=8000)