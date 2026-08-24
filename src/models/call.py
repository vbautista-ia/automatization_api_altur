from datetime import datetime
import enum

from sqlalchemy import ForeignKey
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
    status: Mapped[StatusCall] = mapped_column(SQLEnum(StatusCall, native_enum=False))
    answered_by: Mapped[AnsweredBy] = mapped_column(SQLEnum(AnsweredBy, native_enum=False))
    create_at: Mapped[datetime | None]
    started_at: Mapped[datetime | None]
    ended_at: Mapped[datetime | None]
    ended_by: Mapped[EndedBy | None] = mapped_column(SQLEnum(EndedBy, native_enum=False))
    ended_reason: Mapped[str]
    duration: Mapped[int]
    billed_duration: Mapped[int]
    
    campaign_id: Mapped[int] = mapped_column(ForeignKey('campaigns.id'))
    campaign_belonging: Mapped["Campaign"] = relationship(back_populates='calls')
    
    contact_id: Mapped[int] = mapped_column(ForeignKey('contacts.id'))
    call_contact: Mapped['Contact'] = relationship(back_populates='calls')