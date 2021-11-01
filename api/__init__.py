import fastapi


def include_routers(app: fastapi.FastAPI):
    from . import (
        account,
        profile,
        friend,
        category,
    )

    app.include_router(account.router)
    app.include_router(profile.router)
    app.include_router(friend.router)
    app.include_router(category.router)
