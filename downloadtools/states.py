from enum import Enum


class ProcessState(Enum):
    EXIT = 0
    SLEEP = 1
    PROCESS = 2


class ResultState(Enum):
    SUCCESS = 0
    FAILED = 1
    SPECIAL_CASE_URL = 2
