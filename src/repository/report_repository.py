from sqlalchemy import String, select, Date
from sqlalchemy.orm import Session

from models.campaign import Campaign
from models.contact import Contact

class ReportRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def get_contacts(self, start: str, end: str, agents: list[str]) -> list[dict]:
        """
        Obtiene los contactos filtrados por rango de fecha de inicio de campaña y agentes.
        """
        stmt = (
            select(
                Campaign.name.label("campaign_name"),
                Campaign.created_at.cast(Date).label("campaign_date"),
                Contact.f_id.label('id'),
                Contact.contact,
                Contact.name,
                Contact.context,
                Contact.status.cast(String).label('status'),
                Contact.retries,
                Contact.call_count.label("calls"),
                Contact.billed_duration,
                Contact.last_call_at.label("last_update"),
                Contact.has_follow_up.label('follow_up'), 
                Contact.tags,
                Contact.extracted_data
            )
            .join(Contact, Contact.campaign_id == Campaign.id)
            .where(
                Campaign.started_at >= start,
                Campaign.started_at < end,
                Campaign.agent_id.in_(agents)
            )
            .order_by(Campaign.name.desc())
        )

        result = self.db.execute(stmt).mappings().all()
        return [dict(row) for row in result]