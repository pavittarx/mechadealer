import logging
import os
from contextlib import asynccontextmanager
from typing import Annotated, Dict, TypedDict

import jwt
from dotenv import load_dotenv
from fastapi import FastAPI, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from storelib import Store, Users, init_db

# Services own configuration loading; the libraries only read the environment.
load_dotenv()

JWT_SECRET = os.getenv("JWT_SECRET")
jwt_algorithm = "HS256"
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())

# Comma-separated list, so the deployed frontend origin can be configured
# without a code change.
CORS_ORIGINS = [
    origin.strip()
    for origin in os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
    if origin.strip()
]


# Creating the schema on startup is convenient locally but wasteful where the
# process starts per request, so it can be turned off once the schema exists.
INIT_DB_ON_STARTUP = os.getenv("INIT_DB_ON_STARTUP", "1").lower() not in {
    "0",
    "false",
    "no",
}


@asynccontextmanager
async def lifespan(_: FastAPI):
    if not JWT_SECRET:
        raise RuntimeError("JWT_SECRET is not set in the environment variables.")

    if INIT_DB_ON_STARTUP:
        # storelib no longer issues DDL on import, so the service asks for it.
        init_db()
        logger.info("[app_server]: schema ready")

    yield


app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
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


def _jwt_secret() -> str:
    # Validated at startup by the lifespan handler; narrowed here so the
    # signing calls are not typed against `str | None`.
    if not JWT_SECRET:
        raise RuntimeError("JWT_SECRET is not set in the environment variables.")

    return JWT_SECRET


def _bearer_token(header: str | None) -> str:
    """Pull the token out of an Authorization header.

    `header.split(" ")[1]` raised IndexError on a malformed header, which
    surfaced to the client as "list index out of range".
    """
    if not header:
        raise ValueError("Authorization header is missing")

    scheme, _, token = header.partition(" ")

    if scheme.lower() != "bearer" or not token.strip():
        raise ValueError("Authorization header must be a Bearer token")

    return token.strip()


def encode_jwt(data: Dict[str, int | str]) -> str:
    return jwt.encode(
        data,
        _jwt_secret(),
        algorithm=jwt_algorithm,
    )


def decode_jwt(token: str) -> TokenData:
    payload = jwt.decode(
        token,
        _jwt_secret(),
        algorithms=[jwt_algorithm],
    )

    return TokenData(user_id=payload["user_id"], username=payload["username"])


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
    Authorization: Annotated[str | None, Header(convert_underscores=False)] = None,
):
    try:
        token = _bearer_token(Authorization)
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
    Authorization: Annotated[str | None, Header(convert_underscores=False)] = None,
):
    try:
        token = _bearer_token(Authorization)
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
    req: ReqInvestIntoStrategy,
    Authorization: Annotated[str | None, Header(convert_underscores=False)] = None,
):
    try:
        token = _bearer_token(Authorization)
        data = decode_jwt(token)

        strategy = store.get_strategy(strategy_id=req.strategy_id)

        if strategy is None:
            raise Exception("Strategy not found")

        store.invest_in_strategy(
            strategy_id=req.strategy_id,
            user_id=data["user_id"],
            amount=req.amount,
        )

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
    req: ReqInvestIntoStrategy,
    Authorization: Annotated[str | None, Header(convert_underscores=False)] = None,
):
    try:
        token = _bearer_token(Authorization)
        data = decode_jwt(token)

        strategy = store.get_strategy(strategy_id=req.strategy_id)

        if strategy is None:
            raise Exception("Strategy not found")

        store.withdraw_from_strategy(
            strategy_id=req.strategy_id,
            user_id=data["user_id"],
            amount=req.amount,
        )

        return {
            "is_error": False,
            "is_success": True,
            "message": "Amount withdrawn from strategy successfully",
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
