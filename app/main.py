"""
See the NOTICE file distributed with this work for additional information
regarding copyright ownership.


Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
import fastapi_plugins
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from api.resources.routes import router
from core.config import API_PREFIX, ALLOWED_HOSTS, VERSION, PROJECT_NAME, DEBUG, config


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


# class AppSettings(config, fastapi_plugins.RedisSettings):
#     api_name: str = str(__name__)
#

app = get_application()
# config = AppSettings()


# @app.on_event('startup')
# async def on_startup() -> None:
#     await fastapi_plugins.redis_plugin.init_app(app)
#     await fastapi_plugins.redis_plugin.init()
#
#
# @app.on_event('shutdown')
# async def on_shutdown() -> None:
#     await fastapi_plugins.redis_plugin.terminate()
