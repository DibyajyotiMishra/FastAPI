import json
from typing import Annotated

from db import SessionLocal
from fastapi import Depends, Path, APIRouter
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from models import Todo
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from .auth import get_current_user

router = APIRouter(
    prefix="/todo",
    tags=["todos"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


class TodoRequest(BaseModel):
    title: str = Field(min_length=3)
    description: str = Field(min_length=3, max_length=1000)
    priority: int = Field(gt=0, lt=4)
    complete: bool


@router.get("/")
async def get_all_todos(user_resp: user_dependency, db: db_dependency):
    status_code = int(user_resp.status_code)
    if status_code != 200:
        return JSONResponse(status_code=401, content="Authentication Failed!")
    user = json.loads(user_resp.body)
    todos = []
    if user.get('role') == 'admin':
        todos = db.query(Todo).all()
    else:
        todos = db.query(Todo).filter(Todo.owner_id == user.get('id')).all()
    return JSONResponse(status_code=200, content=jsonable_encoder(todos))


@router.get("/{todo_id}")
async def get_todo_by_id(user_resp: user_dependency, db: db_dependency, todo_id: int = Path(gt=0)):
    status_code = int(user_resp.status_code)
    if status_code != 200:
        return JSONResponse(status_code=401, content="Authentication Failed!")
    user = json.loads(user_resp.body)
    todo_model = db.query(Todo).filter(Todo.id == todo_id).filter(Todo.owner_id == user.get('id')).first()
    if todo_model is not None:
        return JSONResponse(status_code=200, content=jsonable_encoder(todo_model))
    return JSONResponse(status_code=404, content="No match found!")


@router.post("/add")
async def create_todo(user_resp: user_dependency, db: db_dependency, todo_request: TodoRequest):
    status_code = int(user_resp.status_code)
    if status_code != 200:
        return JSONResponse(status_code=401, content="Authentication Failed!")
    user = json.loads(user_resp.body)
    todo_model = Todo(**todo_request.model_dump(), owner_id=user.get('id'))
    db.add(todo_model)
    db.commit()
    return JSONResponse(status_code=201, content="New Todo created!")


@router.put("/update/{todo_id}")
async def update_todo(
        user_resp: user_dependency,
        db: db_dependency,
        todo_request: TodoRequest,
        todo_id: int = Path(gt=0)
):
    status_code = int(user_resp.status_code)
    if status_code != 200:
        return JSONResponse(status_code=401, content="Authentication Failed!")
    user = json.loads(user_resp.body)
    todo_model = db.query(Todo).filter(Todo.id == todo_id).filter(Todo.owner_id == user.get('id')).first()
    if todo_model is None:
        return JSONResponse(status_code=404, content="No match found!")

    todo_model.title = todo_request.title
    todo_model.description = todo_request.description
    todo_model.priority = todo_request.priority
    todo_model.complete = todo_request.complete

    db.add(todo_model)
    db.commit()
    return JSONResponse(status_code=201, content="Todo is updated!")


@router.delete("/delete/{todo_id}")
async def delete_todo(
        user_resp: user_dependency,
        db: db_dependency,
        todo_id: int = Path(gt=0)
):
    status_code = int(user_resp.status_code)
    if status_code != 200:
        return JSONResponse(status_code=401, content="Authentication Failed!")
    user = json.loads(user_resp.body)
    todo_model = db.query(Todo).filter(Todo.id == todo_id).filter(Todo.owner_id == user.get('id')).first()
    if todo_model is None:
        return JSONResponse(status_code=404, content="No match found!")

    db.query(Todo).filter(Todo.id == todo_id).delete()
    db.commit()
    return JSONResponse(status_code=201, content="Todo is deleted!")
