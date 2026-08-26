from datetime import datetime
import enum
from typing import Any

from sqlalchemy import JSON, DateTime, ForeignKey
from sqlalchemy import Enum as SQLEnum

from config.database import Base

from sqlalchemy.orm import Mapped, mapped_column, relationship

class StatusContact(enum.Enum):
    QUEUE= 'queue'
    SENDING = 'sending'
    SENT = 'sent'
    DELIVERED = 'delivered'
    VOICEMAIL = 'voicemail'
    READ = 'read'
    FAILED = 'failed'
    RETRYING = 'retrying'
    CONVERTED = 'converted'
    ANSWERED = 'answered'
    ACCEPTED = 'accepted'
    REJECTED = 'rejected'

class Contact(Base):
    __tablename__ = 'contacts'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=False, index=True)
    f_id: Mapped[str]
    name: Mapped[str]
    contact: Mapped[str]
    status: Mapped[StatusContact] = mapped_column(SQLEnum(StatusContact, native_enum=False))
    context: Mapped[str]
    retries: Mapped[int]
    has_follow_up: Mapped[bool]
    call_count: Mapped[int]
    billed_duration: Mapped[int]
    last_call_at: Mapped[datetime | None] = mapped_column(DateTime(True))
    
    extracted_data: Mapped[dict[str, Any]] = mapped_column(type_=JSON)
    tags: Mapped[list[str]] = mapped_column(type_=JSON)
    
    campaign_id: Mapped[int] = mapped_column(ForeignKey('campaigns.id'))
    assigned_camp: Mapped["Campaign"] = relationship(back_populates='contacts')
    
    calls: Mapped[list['Call']] = relationship(back_populates="call_contact")