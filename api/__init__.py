import fastapi


def include_routers(app: fastapi.FastAPI):
    from . import (
        account,
        profile,
    )

    app.include_router(account.router)
    app.include_router(profile.router)
