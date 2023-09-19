#!/usr/bin/python3

import uvicorn
from fastapi import FastAPI
from aproc.service.aproc_services import AprocServices

from aproc.service.exception_handler import EXCEPTION_HANDLERS
from aproc.service.ogc_processes_api import ROUTER

app = FastAPI()
app.include_router(ROUTER)

for eh in EXCEPTION_HANDLERS:
    app.add_exception_handler(eh.exception, eh.handler)

AprocServices.init("test/conf/aproc.yaml")

uvicorn.run(app)
