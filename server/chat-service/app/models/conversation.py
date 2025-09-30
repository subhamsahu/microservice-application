from pydantic import Field
from beanie import Document
from pymongo import IndexModel


class Conversation(Document):
    conversation_id: str = Field(..., description="Unique conversation ID")
    sender_username: str
    receiver_username: str

    class Settings:
        name = "conversations"
        indexes = [
            IndexModel([("conversation_id", 1)], unique=True),
            IndexModel([("sender_username", 1)]),
            IndexModel([("receiver_username", 1)]),
            IndexModel([("sender_username", 1), ("receiver_username", 1)]),
        ]
