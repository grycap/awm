#!/usr/bin/env python3
import os
import logging
from dotenv import load_dotenv
from fastapi import FastAPI
from awm.routers import deployments


load_dotenv()

LOG_LEVEL = os.getenv("LOG_LEVEL", "info")

# Configurar el logger principal
logging.basicConfig(
    level=LOG_LEVEL.upper(),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

logger = logging.getLogger(__name__)


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
