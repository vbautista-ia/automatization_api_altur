import datetime

from sqlalchemy import text
from sqlalchemy.orm import Session

class NuxibaRepository:
    def __init__(self, db: Session):
        self.nux_db = db
         
    def get_transcriptions(self, campaign: str = None, start: datetime = None, end: datetime = None, min_duration: int = 0):
        query = """
                SELECT 
                    cco.cal_id AS id, cco.totalCall_Time AS duration, cco.cal_Inicio AS start_at,
                    ccodi.name_cal AS result,
                    vdth.Campaña AS campaign, vdth.transcription 
                FROM CCReportsRIA.dbo.ccoCallsOut cco
                INNER JOIN CCReportsRIA.dbo.ccoCallsOutDispositionIA ccodi 
                ON cco.cal_id = ccodi.call_id 
                INNER JOIN CCenterRIA.dbo.view_Detalle_Transcripciones_History vdth 
                ON cco.cal_id = vdth.cal_id 
                WHERE
                    cco.totalCall_Time > :min_duration
                """
        params = {'min_duration': min_duration}
        
        if campaign:
            query += " AND vdth.Campaña LIKE :campaign"
            params['campaign'] = f"%{campaign}%"
        
        if start:
            query += " AND vdth.Fecha >= :start_date"
            params["start_date"] = start
            
        if end:
            query += " AND vdth.Fecha < :end_date"
            params["end_date"] = end
        
        try:
            result = self.nux_db.execute(text(query), params)
            return result.mappings().all()
            
        except Exception as e:
            print("\nError al conectar:")
            print(e)
        
        return []