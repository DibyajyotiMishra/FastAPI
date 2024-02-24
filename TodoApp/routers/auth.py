from datetime import timedelta, datetime
from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.orm import Session
from db import SessionLocal
from models import Users
from pydantic import BaseModel
from passlib.context import CryptContext
from jose import jwt, JWTError

router = APIRouter()

SECRET_KEY = "579158e12ac534d9bfcd88a814a155229cc9d121e580aab972e76c19e6a16a60f74ecb6c4a911472f4fa5fdc94e0918919292f2dbc0e36fe89a35c2f5f8ccdf9"
ALGORITHM = 'HS256'

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='token')

class UserRequest(BaseModel):
    first_name: str
    last_name: str
    username: str
    email: str
    password: str
    role: str


class Token(BaseModel):
    access_token: str
    token_type: str


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


def authenticate_user(username: str, password: str, db):
    user = db.query(Users).filter(Users.username == username).first()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    return user


def create_access_token(username: str, user_id: int, expires_delta: timedelta):
    encode = {
        'sub': username,
        'id': user_id
    }
    expires = datetime.utcnow() + expires_delta
    encode.update({'exp': expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, ALGORITHM)
        username: str = payload.get('sub')
        user_id: int = payload.get('id')
        if user_id is None or username is None:
            return JSONResponse(status_code=403, content="Forbidden!")
        data = {'username': username, 'id': user_id}
        return JSONResponse(status_code=200, content=jsonable_encoder(data))
    except JWTError:
        return JSONResponse(status_code=401, content="Unauthorized!")



@router.post("/auth/")
async def create_user(db: db_dependency, create_user_request: UserRequest):
    user_model = Users(
        first_name=create_user_request.first_name,
        last_name=create_user_request.last_name,
        username=create_user_request.username,
        email=create_user_request.email,
        hashed_password=bcrypt_context.hash(create_user_request.password),
        role=create_user_request.role,
        is_active=True
    )

    db.add(user_model)
    db.commit()
    return JSONResponse(status_code=201, content="User added!")


@router.post("/token", response_model=Token)
async def login_for_access_token(db: db_dependency, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        return JSONResponse(status_code=403, content="Forbidden!")

    token = create_access_token(user.username, user.id, timedelta(minutes=20))
    return {'access_token': token, 'token_type': 'bearer'}
