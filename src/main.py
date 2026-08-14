from datetime import datetime
import logging
import os
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import pandas as pd

# from configuration.platforms import Platforms
# from service.call_assets_service import CallAssetsService
# from service.call_service import CallService
# from service.report_service import ReportService

from controller.report_controller import router as router_report 
from controller.campaign_controller import router as router_campaign 
from controller.call_controller import call_router

logging.basicConfig(
    level=logging.INFO, # Captura todos los mensajes (desde DEBUG hasta CRITICAL)
    # format='%(asctime)s - %(levelname)s - %(message)s' # Muestra fecha, nivel y texto
)

app = FastAPI()
app.include_router(router=router_report)
app.include_router(router=router_campaign)
app.include_router(router=call_router)

@app.get('/', )
async def index():
    return FileResponse(path='static/index.html')