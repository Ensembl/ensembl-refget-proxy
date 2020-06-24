from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from api.resources.routes import router
from core.config import API_PREFIX, ALLOWED_HOSTS, VERSION, PROJECT_NAME, DEBUG


def get_application() -> FastAPI:
    application = FastAPI(title=PROJECT_NAME, debug=DEBUG, version=VERSION)

    application.add_middleware(
        CORSMiddleware,
        allow_origins=ALLOWED_HOSTS or ["*"],
        allow_credentials=True,
        allow_methods=["GET"],
        allow_headers=["*"],
    )

    application.include_router(router, prefix=API_PREFIX)

    return application


app = get_application()
