from typing import Annotated

from fastapi import FastAPI, Depends, Path
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

import models
from db import engine, SessionLocal
from models import Todo

app = FastAPI()

models.Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


class TodoRequest(BaseModel):
    title: str = Field(min_length=3)
    description: str = Field(min_length=3, max_length=1000)
    priority: int = Field(gt=0, lt=4)
    complete: bool


@app.get("/")
async def get_all_todos(db: db_dependency):
    return JSONResponse(status_code=200, content=jsonable_encoder(db.query(Todo).all()))


@app.get("/todo/{todo_id}")
async def get_todo_by_id(db: db_dependency, todo_id: int = Path(gt=0)):
    todo_model = db.query(Todo).filter(Todo.id == todo_id).first()
    if todo_model is not None:
        return JSONResponse(status_code=200, content=jsonable_encoder(todo_model))
    return JSONResponse(status_code=404, content="No match found!")


@app.post("/todo/add")
async def create_todo(db: db_dependency, todo_request: TodoRequest):
    todo_model = Todo(**todo_request.model_dump())
    db.add(todo_model)
    db.commit()
    return JSONResponse(status_code=201, content="New Todo created!")


@app.put("/todo/update/{todo_id}")
async def update_todo(
        db: db_dependency,
        todo_request: TodoRequest,
        todo_id: int = Path(gt=0)
):
    todo_model = db.query(Todo).filter(Todo.id == todo_id).first()
    if todo_model is None:
        return JSONResponse(status_code=404, content="No match found!")

    todo_model.title = todo_request.title
    todo_model.description = todo_request.description
    todo_model.priority = todo_request.priority
    todo_model.complete = todo_request.complete

    db.add(todo_model)
    db.commit()
    return JSONResponse(status_code=201, content="Todo is updated!")


@app.delete("/todo/delete/{todo_id}")
async def delete_todo(
        db: db_dependency,
        todo_id: int = Path(gt=0)
):
    todo_model = db.query(Todo).filter(Todo.id == todo_id).first()
    if todo_model is None:
        return JSONResponse(status_code=404, content="No match found!")

    db.query(Todo).filter(Todo.id == todo_id).delete()
    db.commit()
    return JSONResponse(status_code=201, content="Todo is deleted!")
