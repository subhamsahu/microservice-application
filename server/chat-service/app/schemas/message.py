from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class Offer(BaseModel):
    catalog_title: Optional[str] = None
    price: Optional[float] = None
    description: Optional[str] = None
    delivery_in_days: Optional[int] = None
    old_delivery_date: Optional[str] = None
    new_delivery_date: Optional[str] = None
    accepted: Optional[bool] = None
    cancelled: Optional[bool] = None


class MessageSchema(BaseModel):
    conversation_id: Optional[str] = None
    id: Optional[str] = None
    body: Optional[str] = None
    has_conversation_id: Optional[bool] = None
    file: Optional[str] = None
    file_type: Optional[str] = None
    file_name: Optional[str] = None
    file_size: Optional[str] = None
    catalog_id: Optional[str] = None
    seller_id: str = Field(..., description="Seller id is required")
    buyer_id: str = Field(..., description="Buyer id is required")
    sender_username: str = Field(..., description="Sender username is required")
    sender_picture: str = Field(..., description="Sender picture is required")
    receiver_username: str = Field(..., description="Receiver username is required")
    receiver_picture: str = Field(..., description="Receiver picture is required")
    is_read: Optional[bool] = False
    has_offer: Optional[bool] = False
    offer: Optional[Offer] = None
    created_at: Optional[datetime] = None

    class Config:
        orm_mode = True
