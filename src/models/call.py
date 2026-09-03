from datetime import datetime
import enum
from typing import Any

from sqlalchemy import JSON, DateTime, ForeignKey
from sqlalchemy import Enum as SQLEnum

from config.database import Base

from sqlalchemy.orm import Mapped, mapped_column, relationship


class StatusCall(enum.Enum):
    ENDED = 'ended'
    FAILED = 'failed'
    BUSY = 'busy'
    NO_ANSWER = 'no-answer'
    IN_PROGRESS = 'in-progress'

class AnsweredBy(enum.Enum):
    HUMAN = 'human'
    MACHINE = 'machine'
    UNKNOWN = 'unknown'

class EndedBy(enum.Enum):
    AGENT = 'agent'
    USER = 'user'
    SYSTEM = 'system'
    
class Call(Base):
    __tablename__ = 'calls'
    
    id: Mapped[str] = mapped_column(primary_key=True, autoincrement=False, index=True)
    type: Mapped[str]
    status: Mapped[StatusCall] = mapped_column(SQLEnum(StatusCall, native_enum=False, values_callable=lambda obj: [e.value for e in obj]))
    answered_by: Mapped[AnsweredBy] = mapped_column(SQLEnum(AnsweredBy, native_enum=False, values_callable=lambda obj: [e.value for e in obj]))
    create_at: Mapped[datetime | None] = mapped_column(DateTime(True))
    started_at: Mapped[datetime | None] = mapped_column(DateTime(True))
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(True))
    ended_by: Mapped[EndedBy | None] = mapped_column(SQLEnum(EndedBy, native_enum=False, values_callable=lambda obj: [e.value for e in obj]))
    ended_reason: Mapped[str]
    duration: Mapped[int]
    billed_duration: Mapped[int]
    
    extracted_data: Mapped[dict[str, Any]] = mapped_column(type_=JSON)
    tags: Mapped[list[str]] = mapped_column(type_=JSON)
    
    campaign_id: Mapped[int] = mapped_column(ForeignKey('campaigns.id'))
    campaign_belonging: Mapped["Campaign"] = relationship(back_populates='calls')
    
    contact_id: Mapped[int] = mapped_column(ForeignKey('contacts.id'))
    call_contact: Mapped['Contact'] = relationship(back_populates='calls')