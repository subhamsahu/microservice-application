from typing import Optional
from datetime import datetime
from pydantic import Field
from beanie import Document
from pymongo import IndexModel


class Offer(Document):
    catalog_title: str = Field(default="")
    price: float = Field(default=0)
    description: str = Field(default="")
    delivery_in_days: int = Field(default=0)
    old_delivery_date: str = Field(default="")
    new_delivery_date: str = Field(default="")
    accepted: bool = Field(default=False)
    cancelled: bool = Field(default=False)

    class Settings:
        name = "offers"


class Message(Document):
    conversation_id: str
    sender_username: str
    receiver_username: str
    sender_picture: str
    receiver_picture: str
    body: Optional[str] = ""
    file: Optional[str] = ""
    file_type: Optional[str] = ""
    file_size: Optional[str] = ""
    file_name: Optional[str] = ""
    catalog_id: Optional[str] = ""
    buyer_id: str
    seller_id: str
    is_read: bool = False
    has_offer: bool = False
    offer: Offer = Field(default_factory=Offer)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "messages"
        indexes = [
            IndexModel([("conversation_id", 1)]),
            IndexModel([("sender_username", 1)]),
            IndexModel([("receiver_username", 1)]),
            IndexModel([("created_at", -1)]),
            IndexModel([("conversation_id", 1), ("created_at", -1)]),
        ]
