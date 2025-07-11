from fastapi import FastAPI, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Annotated, TypedDict
from storelib import Store, Users
import jwt
import os
import logging

JWT_SECRET = os.getenv("JWT_SECRET")
jwt_algorithm = "HS256"
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

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


class ReqInvestIntoStrategy(BaseModel):
    strategy_id: int
    amount: float


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


@app.get("/user/strategies")
def get_user_strategies(
    Authorization: Annotated[str | None, Header(convert_underscores=False)],
):
    try:
        if not Authorization:
            raise Exception("Authorization header is missing")

        token = Authorization.split(" ")[1]
        data = decode_jwt(token)

        res = store.get_user_strategies(data["user_id"])

        if not res:
            raise Exception("No strategies found for the user")

        return {
            "is_error": False,
            "is_success": True,
            "message": "User strategies fetched successfully",
            "data": [row._mapping for row in res],
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
            "message": "User Details fetched successfully",
            "data": res,
        }
    except Exception as e:
        return {
            "is_error": True,
            "is_success": False,
            "message": str(e),
            "data": None,
        }


@app.get("/strategies")
def get_strategies():
    try:
        res = store.get_strategies()

        if not res:
            raise Exception("Strategies not found")

        res = [row._mapping for row in res]

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


@app.post("/strategies/invest")
def invest_into_strategy(
    Authorization: Annotated[str | None, Header(convert_underscores=False)],
    req: ReqInvestIntoStrategy,
):
    try:
        if not Authorization:
            raise Exception("Authorization header is missing")

        token = Authorization.split(" ")[1]
        data = decode_jwt(token)

        strategy = store.get_user_strategies(req.strategy_id)

        if not strategy:
            raise Exception("Strategy not found")

        store.invest_in_strategy(data["user_id"], req.strategy_id, req.amount)

        return {
            "is_error": False,
            "is_success": True,
            "message": "Amount added to strategy successfully",
            "data": None,
        }
    except Exception as e:
        return {
            "is_error": True,
            "is_success": False,
            "message": str(e),
            "data": None,
        }


@app.post("/strategies/withdraw")
def wothdraw_from_strategy(
    Authorization: Annotated[str | None, Header(convert_underscores=False)],
    req: ReqInvestIntoStrategy,
):
    try:
        if not Authorization:
            raise Exception("Authorization header is missing")

        token = Authorization.split(" ")[1]
        data = decode_jwt(token)

        strategy = store.get_user_strategies(req.strategy_id)

        if not strategy:
            raise Exception("Strategy not found")

        store.withdraw_from_strategy(data["user_id"], req.strategy_id, req.amount)

        return {
            "is_error": False,
            "is_success": True,
            "message": "Amount added to strategy successfully",
            "data": None,
        }
    except Exception as e:
        return {
            "is_error": True,
            "is_success": False,
            "message": str(e),
            "data": None,
        }


@app.get("/strategies/{strategy_id}")
def get_strategy_by_id(strategy_id: int):
    try:
        res = store.get_strategy(strategy_id)

        if not res:
            raise Exception("Strategy not found")

        return {
            "is_error": False,
            "is_success": True,
            "message": "Strategy fetched successfully",
            "data": res._mapping,
        }
    except Exception as e:
        return {
            "is_error": True,
            "is_success": False,
            "message": str(e),
            "data": None,
        }
