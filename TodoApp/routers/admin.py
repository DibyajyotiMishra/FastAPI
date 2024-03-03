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
    prefix="/admin",
    tags=["admin"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


@router.get("/todo")
async def get_all_admin_todos(user_resp: user_dependency, db:db_dependency):
    if user_resp is None or json.loads(user_resp.body).get('role') != 'admin':
        return JSONResponse(status_code=401, content="Authentication Failed")
    return JSONResponse(status_code=200, content=db.query(Todo).all())


@router.delete("/todo/{todo_id}")
async def delete_todo(user_resp: user_dependency, db: db_dependency, todo_id: int = Path(gt=0)):
    if user_resp is None or json.loads(user_resp.body).get('role') != 'admin':
        return JSONResponse(status_code=401, content="Authentication Failed")
    todo_model = db.query(Todo).filter(Todo.id == todo_id).first()
    if todo_model is None:
        return JSONResponse(status_code=404, content="No such todo found in the db")
    db.query(Todo).filter(Todo.id == todo_id).delete()
    db.commit()
    return JSONResponse(status_code=201, content="Todo deleted successfully")
