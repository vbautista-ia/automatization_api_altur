from datetime import datetime
import enum

from config.database import Base

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import DateTime, Enum as SQLEnum


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
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=False, index=True)
    name: Mapped[str]
    description: Mapped[str]
    status: Mapped[StatusCampaign] = mapped_column(SQLEnum(StatusCampaign, native_enum=False))
    created_at: Mapped[datetime] = mapped_column(DateTime(True))
    started_at: Mapped[datetime | None] = mapped_column(DateTime(True))
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(True))

    agent: Mapped[str]

    timezone: Mapped[str]
    retries: Mapped[int]
    archived: Mapped[bool]
    first_message: Mapped[str]
    
    calls: Mapped[list['Call']] = relationship(back_populates='campaign_belonging')
    contacts: Mapped[list['Contact']] = relationship(back_populates='assigned_camp')