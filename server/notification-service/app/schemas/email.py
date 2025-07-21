from typing import Optional
from pydantic import BaseModel

class EmailMessage(BaseModel):
    sender: Optional[str] = None
    appLink: str
    appIcon: str
    offerLink: Optional[str] = None
    amount: Optional[str] = None
    buyerUsername: Optional[str] = None
    sellerUsername: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    deliveryDays: Optional[str] = None
    orderId: Optional[str] = None
    orderDue: Optional[str] = None
    requirements: Optional[str] = None
    orderUrl: Optional[str] = None
    originalDate: Optional[str] = None
    newDate: Optional[str] = None
    reason: Optional[str] = None
    subject: Optional[str] = None
    header: Optional[str] = None
    type: Optional[str] = None
    message: Optional[str] = None
    serviceFee: Optional[str] = None
    total: Optional[str] = None
    username: Optional[str] = None
    verifyLink: Optional[str] = None
    resetLink: Optional[str] = None
