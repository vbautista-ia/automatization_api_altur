import logging

from fastapi import FastAPI
from fastapi.responses import FileResponse

from controller.report_controller import router as router_report 
from controller.campaign_controller import router as router_campaign 
from controller.call_controller import call_router
from controller.data_importer_controller import data_router


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)

app = FastAPI()
app.include_router(router=router_report)
app.include_router(router=router_campaign)
app.include_router(router=call_router)
app.include_router(router=data_router)

@app.get('/', )
async def index():
    return FileResponse(path='static/index.html')