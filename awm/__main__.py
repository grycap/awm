#!/usr/bin/env python3
import os
import logging
from dotenv import load_dotenv
from fastapi import FastAPI
from awm.routers import deployments, allocations, tools, service, users


load_dotenv()

LOG_LEVEL = os.getenv("LOG_LEVEL", "info")

# Configurar el logger principal
logging.basicConfig(
    level=LOG_LEVEL.upper(),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

logger = logging.getLogger(__name__)


def create_app():
    app = FastAPI(
        title="EOSC AWM API",
        description="EOSC Application Workflow Management API",
        version="1.0.0"
    )

    app.include_router(
        deployments.router,
        prefix="/deployments",
        tags=["Deployments"]
    )

    app.include_router(
        allocations.router,
        prefix="/allocations",
        tags=["Allocations"]
    )

    app.include_router(
        tools.router,
        prefix="/tools",
        tags=["Tools"]
    )

    app.include_router(
        service.router,
        prefix="/service",
        tags=["Service"]
    )

    app.include_router(
        users.router,
        prefix="/user",
        tags=["Users"]
    )

    return app


def main():
    import uvicorn
    uvicorn.run(create_app(), host="127.0.0.1", port=8080)


if __name__ == '__main__':
    main()
