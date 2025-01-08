from enum import Enum


class AiDataEnum(Enum):
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
    RUNNING = "running"
    QUEUED = "queued"
    SYSTEM = "system"
    FLAGS = "flags"
