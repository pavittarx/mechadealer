import bcrypt
from sqlalchemy.exc import SQLAlchemyError

from ._setup import get_engine
from ._tables import user_transactions, users
from .models import User


class Users:
    def _hash_password(self, password: str) -> str:
        # Placeholder for password encryption logic
        hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
        return hash.decode("utf-8")

    def _verify_password(self, password: str, hashed_password: str) -> bool:
        # Placeholder for password verification logic
        return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))

    def create_user(self, name: str, password: str, username: str, capital: float = 0):
        with get_engine().connect() as conn:
            query = users.select().where(users.c.username == username)
            if conn.execute(query).fetchone() is not None:
                raise ValueError("User already exists")

            # RETURNING is required: without it the INSERT result has no rows,
            # so this returned None and /register responded with `null` even
            # though the user had been created.
            ins = (
                users.insert()
                .values(
                    name=name,
                    password=self._hash_password(password),
                    username=username,
                    capital=capital,
                )
                .returning(users.c.id)
            )

            result = conn.execute(ins).fetchone()
            conn.commit()

            if result is None:
                return None

            return {
                "id": result.id,
                "name": name,
                "username": username,
                "capital": capital,
            }

    def login(self, username: str, password: str):
        if not username or not password:
            raise ValueError("Username and password are required")

        with get_engine().connect() as conn:
            query = users.select().where(users.c.username == username)
            user = conn.execute(query).fetchone()

        if user and self._verify_password(password, user.password):
            return User(
                id=user.id,
                name=user.name,
                username=user.username,
                email=user.email,
                capital=user.capital,
            )
        else:
            raise Exception("Invalid User or Credentials")

    def get_user(self, user_id: int):
        if not user_id:
            raise ValueError("User ID is required")

        with get_engine().connect() as conn:
            query = users.select().where(users.c.id == user_id)
            result = conn.execute(query).fetchone()

        if result is not None:
            return User(
                id=result.id,
                name=result.name,
                username=result.username,
                capital=result.capital,
                capital_used=result.capital_used,
            )
        else:
            print("User Not found")
            return None

    def _adjust_funds(self, user_id: int, amount: float, kind: str):
        """Record a transaction and move the user's capital by `amount`.

        `kind` must match the user_transactions check constraint.
        """
        if not user_id or not amount:
            raise ValueError("User ID and amount are required")

        sign = 1 if kind == "deposit" else -1

        with get_engine().connect() as conn:
            try:
                user_details_query = users.select().where(users.c.id == user_id)
                user_details_result = conn.execute(user_details_query).fetchone()

                if not user_details_result:
                    raise ValueError(f"User with ID {user_id} not found.")

                trans_ins = user_transactions.insert().values(
                    user_id=user_id,
                    type=kind,
                    amount=amount,
                )
                conn.execute(trans_ins)

                user_update = (
                    users.update()
                    .where(users.c.id == user_id)
                    .values(
                        capital=users.c.capital + (sign * amount),
                    )
                )
                conn.execute(user_update)

                conn.commit()
                return True

            except ValueError as ve:
                print(f"ValueError in _adjust_funds({kind}): {ve}")
                raise
            except SQLAlchemyError as e:
                print(f"Database error in _adjust_funds({kind}), rolling back: {e}")
                conn.rollback()
                raise
            except Exception as e:
                print(f"Unexpected error in _adjust_funds({kind}), rolling back: {e}")
                conn.rollback()
                raise

    def add_funds(self, user_id: int, amount: float):
        return self._adjust_funds(user_id, amount, "deposit")

    def withdraw_funds(self, user_id: int, amount: float):
        # Note the spelling: the user_transactions check constraint declares
        # 'withdrawl'. This previously recorded withdrawals as 'deposit'.
        return self._adjust_funds(user_id, amount, "withdrawl")
