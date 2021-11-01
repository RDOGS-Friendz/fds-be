import fastapi


def include_routers(app: fastapi.FastAPI):
    from . import (
        account,
        profile,
        friend,
        category,
        location,
        event,
    )

    app.include_router(account.router)
    app.include_router(profile.router)
    app.include_router(friend.router)
    app.include_router(category.router)
    app.include_router(location.router)
    app.include_router(event.router)
