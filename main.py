from src.volleyme.infra.db import repos
from src.common import models
from src.volleyme.domain import types, aggregates, enums
import asyncio


async def main():
    async with models.get_db_session_context() as db_session:
        repo = repos.UserRepo(db_session)
        user = aggregates.User(email="user4@volleyme.net", password="123")
        profile = aggregates.Profile(
            user=user,
            first_name="FN",
            last_name="LN",
            avatar_url="https://www.example.com/",
        )
        user.profile = profile
        user = await repo.save_user(user)
    assert True


if __name__ == "__main__":
    asyncio.run(main())
