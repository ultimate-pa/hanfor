from enum import Enum


class Progress(Enum):
    STATUS = "status"
    PROCESSED = "processed"
    TOTAL = "total"
    NOT_STARTED = "not_started"
    ERROR = "error"
    PENDING = "pending"
    CLUSTERING = "clustering"
    COMPLETED = "completed"
    CLUSTER = "cluster"
    AI = "ai"
