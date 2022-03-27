
from fastapi import FastAPI

app = FastAPI()


@app.get('/')
async def get_item():
    return "hello world"


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