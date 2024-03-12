import json
from typing import Annotated

from db import SessionLocal
from fastapi import Depends, Path, APIRouter
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from models import Users
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from .auth import get_current_user, UserRequest, bcrypt_context

router = APIRouter(
    prefix="/user",
    tags=["user"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


class UserVerification(BaseModel):
    current_password: str
    new_password: str = Field(min_length=5)


@router.get("/current-user")
async def get_current_user(user_resp: user_dependency, db: db_dependency):
    if user_resp is None:
        return JSONResponse(status_code=401, content="Authentication failed.")
    user_id = int(json.loads(user_resp.body).get('id'))
    user_data = db.query(Users).filter(Users.id == user_id).first()
    if user_data is None:
        return JSONResponse(status_code=404, content="User not found.")
    user_data.hashed_password = None
    return JSONResponse(status_code=200, content=jsonable_encoder(user_data))


@router.put("/update-password")
async def update_password(user_resp: user_dependency, db: db_dependency, user_verification: UserVerification):
    if user_resp is None:
        return JSONResponse(status_code=401, content="Authentication failed.")
    user_id = int(json.loads(user_resp.body).get('id'))
    user_data = db.query(Users).filter(Users.id == user_id).first()
    if user_data is None or not bcrypt_context.verify(user_verification.current_password, user_data.hashed_password):
        return JSONResponse(status_code=404, content="User not found.")
    user_data.hashed_password = bcrypt_context.hash(user_verification.new_password)
    db.add(user_data)
    db.commit()
    return JSONResponse(status_code=201, content="Password updated")


@router.put("/update-phone")
async def update_phone(user_resp: user_dependency, db: db_dependency, phone_num: str):
    if user_resp is None:
        return JSONResponse(status_code=401, content="Authentication failed.")
    user_id = int(json.loads(user_resp.body).get('id'))
    user_data = db.query(Users).filter(Users.id == user_id).first()
    user_data.phone_number = phone_num
    db.add(user_data)
    db.commit()
    return JSONResponse(status_code=201, content="Phone Number updated.")
