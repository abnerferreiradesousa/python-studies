from fastapi import FastAPI, Depends, Response, status, HTTPException
from blog import models
from blog.hashing import Hash
from blog.schemas import Blog, ShowUser, User
from sqlalchemy.orm import Session
from .database import engine


app = FastAPI()

models.Base.metadata.create_all(engine)


def get_db():
    db = Session()
    try:
        yield db
    finally:
        db.close()


@app.post("/blog", status_code=status.HTTP_201_CREATED)
def create(request: Blog, db: Session = Depends(get_db)):
    new_blog = models.Blog(title=request.title, body=request.body)
    db.add(new_blog)
    db.commit()
    db.refresh(new_blog)
    return new_blog


@app.delete("/blog/{id}", status_code=status.HTTP_204_NO_CONTENT)
def destroy(id, db: Session = Depends(get_db)):
    blog = db.query(models.Blog).filter(models.Blog.id == id)

    if not blog.first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Blog with {id} id not found"
        )

    blog.delete(syncronize_session=False)
    db.commit()
    return {"details": "Blog deleted"}


@app.put("/blog/{id}", status_code=status.HTTP_202_ACCEPTED)
def update(id, request: Blog, db: Session):
    blog = db.query(models.Blog).filter(models.Blog.id == id)

    if not blog.first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Blog with {id} id not found"
        )

    blog.update(request)
    db.commit()
    return {"details": "Blog updated"}


@app.get("/blog")
def get_all(db: Session = Depends(get_db)):
    blogs = db.query(models.Blog).all()
    return blogs


@app.get("/blog/{id}", status_code=200)
def get_single_blog(id, response: Response, db: Session = Depends(get_db)):
    blog = db.query(models.Blog).filter(models.Blog.id == id).first()
    if not blog:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"details": f"There's no blog with the provided id - {id}"}
    return blog


# User
@app.post("/user", response_model=ShowUser)
def create_user(request: User, db: Session = Depends(get_db)):
    new_user = models.User(
        name=request.name, password=Hash.bcrypt(request.password), email=request.email
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@app.get("/user/{id}", response_model=ShowUser)
def get_user(id: int, db: Session)