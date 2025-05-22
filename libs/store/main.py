from sqlalchemy.exc import SQLAlchemyError
from tables import users, user_transactions
from models import User
from setup import engine

import bcrypt


class Store:
    def create_strategy(
        self,
        name,
        run_tf,
        capital,
    ):
        pass

    def get_strategy(self):
        pass

    def invest_in_strategy(self):
        pass

    def withdraw_from_strategy(self):
        pass


if __name__ == "__main__":
    pass
