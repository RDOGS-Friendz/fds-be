import fastapi

from . import (
    database,
    models,
    schema,
    types
)


def orm_include_routers(app: fastapi.FastAPI):
    from . import (
        api
    )

    app.include_router(api.router)
