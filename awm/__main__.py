#!/usr/bin/env python3
from fastapi import FastAPI
from awm.routers import deployments, allocations, tools, service

import warnings
warnings.filterwarnings("always", category=DeprecationWarning)

def create_app():
    
    app = FastAPI(
        title="EOSC AWM API",
        description="EOSC Application Workflow Management API",
        version="0.1.46",
        docs_url="/",
    )

    app.include_router(
        deployments.router,
        tags=["Deployments"]
    )

    app.include_router(
        allocations.router,
        tags=["Allocations"]
    )

    app.include_router(
        tools.router,
        tags=["Tools"]
    )

    app.include_router(
        service.router,
        tags=["Service"]
    )

    return app


def main():
    import uvicorn
    uvicorn.run(create_app(), host="127.0.0.1", port=8080)


app = create_app()


if __name__ == '__main__':
    main()
