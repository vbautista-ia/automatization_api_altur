from enum import Enum


class AnsweredBy(Enum):
    HUMAN = 'human',
    MACHINE = 'machine'
    ONKNOWN = 'unknown'