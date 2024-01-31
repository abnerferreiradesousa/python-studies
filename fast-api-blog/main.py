from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn

app = FastAPI()


@app.get("/blog/{id}")
def index(id: int):
    return id


def root(limit):
    return f"number is {limit}"


class Blog(BaseModel):
    title: str
    body: str
    published_at: bool | None


@app.post("/posttest")
def create_post(blog: Blog):
    return blog


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port="9000")
