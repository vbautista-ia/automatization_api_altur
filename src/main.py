import logging
from fastapi import FastAPI
from fastapi.responses import FileResponse

from config.database import Base, engine
from controller.report_controller import router as router_report 
from controller.campaign_controller import router as router_campaign 
from controller.call_controller import call_router

from models.campaign import Campaign

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s' # Muestra fecha, nivel y texto
)

Base.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(router=router_report)
app.include_router(router=router_campaign)
app.include_router(router=call_router)

@app.get('/', )
async def index():
    return FileResponse(path='static/index.html')