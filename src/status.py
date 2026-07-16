from enum import Enum


class StatusCampaign(Enum):
    PENDING = 'pending'
    READY = 'ready'
    ACTIVE = 'active'
    INACTIVE = 'inactive'
    COOLDOWN = 'cooldown'
    FINISHED = 'finished'

class StatusCall(Enum):
    ENDEN = 'ended'
    FAILED = 'failed'
    BUSY  = 'busy'
    NO_ANSWER = 'no-answer'
    IN_PROGRESS = 'in-progress'