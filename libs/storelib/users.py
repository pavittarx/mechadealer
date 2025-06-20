from sqlalchemy.exc import SQLAlchemyError
from storelib.models import User
from _setup import engine
from _tables import users, user_transactions

import bcrypt


class Users:
    def _hash_password(self, password: str) -> str:
        # Placeholder for password encryption logic
        hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
        return hash.decode("utf-8")

    def _verify_password(self, password: str, hashed_password: str) -> bool:
        # Placeholder for password verification logic
        return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))

    def create_user(self, name: str, password: str, username: str, capital: float = 0):
        conn = engine.connect()
        query = users.select().where(users.c.username == username)
        result = conn.execute(query).fetchone()
        if result is not None:
            raise ValueError("User already exists")

        ins = users.insert().values(
            name=name,
            password=self._hash_password(password),
            username=username,
            capital=capital,
        )

        result = conn.execute(ins)
        conn.commit()

        result = result.fetchone()

        if result is not None:
            result = {
                "id": result.id,
                "name": name,
                "username": username,
                "capital": capital,
            }

        return result

    def login(self, username: str, password: str):
        if not username or not password:
            raise ValueError("Username and password are required")

        conn = engine.connect()
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
        conn = engine.connect()
        query = users.select().where(users.c.id == user_id)
        result = conn.execute(query).fetchone()

        if result is not None:
            return User(
                id=result.id,
                name=result.name,
                username=result.username,
                capital=result.capital,
                capital_remaining=result.capital_remaining,
                capital_used=result.capital_used,
            )
        else:
            print("User Not found")
            return None

    def add_funds(self, user_id: int, amount: float):
        if not user_id or not amount:
            raise ValueError("User ID and amount are required")

        conn = engine.connect()
        query = users.select().where(users.c.id == user_id)
        user_details = conn.execute(query).fetchone()

        if user_details is None:
            raise ValueError("User not found")

        with engine.connect() as conn:
            try:
                user_details_query = users.select().where(users.c.id == user_id)
                user_details_result = conn.execute(user_details_query).fetchone()

                if not user_details_result:
                    raise ValueError(f"User with ID {user_id} not found.")

                trans_ins = user_transactions.insert().values(
                    user_id=user_id,
                    type="deposit",
                    amount=amount,
                )
                conn.execute(trans_ins)

                user_update = (
                    users.update()
                    .where(users.c.id == user_id)
                    .values(
                        capital=users.c.capital
                        + amount,  # Atomically increment capital
                        capital_remaining=users.c.capital_remaining + amount,
                    )  # Also update remaining if it's separate
                )
                conn.execute(user_update)

                # 4. If both operations are successful, commit the transaction
                conn.commit()
                print(
                    f"Successfully added {amount} to user {user_id}. New capital: {user_details_result.capital}"
                )
                return True

            except ValueError as ve:  # Catch specific logical errors
                # No rollback needed here as DB operations might not have started or are not the cause
                print(f"ValueError in add_funds: {ve}")
                raise
            except SQLAlchemyError as e:
                print(f"Database error in add_funds, rolling back: {e}")
                conn.rollback()  # Explicit rollback, though 'with' handles it on error
                raise  # Re-raise the exception to be handled by the caller
            except Exception as e:
                print(f"Unexpected error in add_funds, rolling back: {e}")
                conn.rollback()
                raise

    def withdraw_funds(self, user_id: int, amount: float):
        if not user_id or not amount:
            raise ValueError("User ID and amount are required")

        conn = engine.connect()
        query = users.select().where(users.c.id == user_id)
        user_details = conn.execute(query).fetchone()

        if user_details is None:
            raise ValueError("User not found")

        with engine.connect() as conn:
            try:
                user_details_query = users.select().where(users.c.id == user_id)
                user_details_result = conn.execute(user_details_query).fetchone()

                if not user_details_result:
                    raise ValueError(f"User with ID {user_id} not found.")

                trans_ins = user_transactions.insert().values(
                    user_id=user_id,
                    type="deposit",
                    amount=amount,
                )
                conn.execute(trans_ins)

                user_update = (
                    users.update()
                    .where(users.c.id == user_id)
                    .values(
                        capital=users.c.capital
                        - amount,  # Atomically increment capital
                        capital_remaining=users.c.capital_remaining - amount,
                    )  # Also update remaining if it's separate
                )
                conn.execute(user_update)

                # 4. If both operations are successful, commit the transaction
                conn.commit()
                print(
                    f"Successfully withdrawn {amount} from user {user_id}. New capital: {user_details_result.capital}"
                )
                return True

            except ValueError as ve:  # Catch specific logical errors
                # No rollback needed here as DB operations might not have started or are not the cause
                print(f"ValueError in withdraw_funds: {ve}")
                raise
            except SQLAlchemyError as e:
                print(f"Database error in withdraw_funds, rolling back: {e}")
                conn.rollback()  # Explicit rollback, though 'with' handles it on error
                raise  # Re-raise the exception to be handled by the caller
            except Exception as e:
                print(f"Unexpected error in withdraw_funds, rolling back: {e}")
                conn.rollback()
                raise
