from fastapi import FastAPI, Header
from pydantic import BaseModel
from typing import Dict, Annotated, TypedDict

from storelib import Store, Users
import jwt
import os


app = FastAPI()

users = Users()
store = Store()


@app.get("/health")
async def health():
    return {"status": "healthy"}


class Login(BaseModel):
    username: str
    password: str


class RegisterReq(BaseModel):
    username: str
    password: str
    name: str


JWT_SECRET = os.getenv("JWT_SECRET")
jwt_algorithm = "HS256"


TokenData = TypedDict(
    "TokenData",
    {
        "user_id": int,
        "username": str,
    },
)


def encode_jwt(data: Dict[str, int | str]) -> str:
    return jwt.encode(
        data,
        JWT_SECRET,
        algorithm=jwt_algorithm,
    )


def decode_jwt(token: str) -> TokenData:
    return jwt.decode(
        token,
        JWT_SECRET,
        algorithms=[jwt_algorithm],
    )


@app.post("/register")
async def register(req: RegisterReq):
    try:
        res = users.create_user(
            name=req.name,
            username=req.username,
            password=req.password,
            capital=0,
        )

        return res

    except Exception as e:
        return {
            "is_error": True,
            "is_success": False,
            "message": str(e),
            "data": None,
        }


@app.post("/login")
async def login(req: Login):
    try:
        res = users.login(req.username, req.password)

        data = {
            "user_id": res.id,
            "username": res.username,
        }

        token = encode_jwt(data)

        return {
            "is_error": False,
            "is_success": True,
            "message": "Login successful",
            "data": {
                "user_id": res.id,
                "token": token,
                "user": {
                    "id": res.id,
                    "name": res.name,
                    "username": res.username,
                    "capital": res.capital,
                },
            },
        }
    except Exception as e:
        return {
            "is_error": True,
            "is_success": False,
            "message": str(e),
            "data": None,
        }


@app.get("/user/{user_id}")
async def get_user(
    Authorization: Annotated[str | None, Header(convert_underscores=False)],
):
    try:
        if not Authorization:
            raise Exception("Authorization header is missing")

        token = Authorization.split(" ")[1]
        data = decode_jwt(token)

        res = users.get_user(data["user_id"])

        if not res:
            raise Exception("User not found")

        return {
            "is_error": False,
            "is_success": True,
            "message": "Strategies fetched successfully",
            "data": res,
        }
    except Exception as e:
        return {
            "is_error": True,
            "is_success": False,
            "message": str(e),
            "data": None,
        }
