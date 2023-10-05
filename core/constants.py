from enum import Enum


class BoxConstant(Enum):
    BOX_250 = "250 G"
    BOX_500 = "500 G"
    BOX_1000 = "1 KG"
    BOX_2000 = "2 KG"


class OrderConstant(Enum):
    STATUS_PENDING = "pending"
    STATUS_READY = "ready"
    STATUS_DELIVERED = "delivered"
    STATUS_CANCELLED = "cancelled"
