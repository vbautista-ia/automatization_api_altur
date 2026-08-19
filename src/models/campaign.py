from datetime import date
import enum

from config.database import Base

from sqlalchemy.orm import Mapped, mapped_column


class StatusCampaign(enum.Enum):
    PENDING = 'pending'
    READY = 'ready'
    ACTIVE = 'active'
    INACTIVE = 'inactive'
    COOLDOWN = 'cooldown'
    FINISHED = 'finished'
    
class Integration(enum.Enum):
    PHONE_CALL = 'phone_call'
    WHATSAPP = 'whatsapp'

class Campaign(Base):
    __tablename__ = 'campaigns'
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    campaign_id: Mapped[int] = mapped_column(unique=True)
    name: Mapped[str]
    description: Mapped[str]
    status: Mapped[StatusCampaign]
    created_at: Mapped[date]
    started_at: Mapped[date]
    ended_at: Mapped[date]
    
    agent_id: Mapped[int]
    agent_name: Mapped[str]
    
    timezone: Mapped[date]
    retries: Mapped[date]
    archived: Mapped[bool]
    first_message: Mapped[str]