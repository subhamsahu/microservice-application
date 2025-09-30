"""Chat service for handling chat operations"""
import json
from datetime import datetime
from typing import List, Optional, Dict, Any
from bson import ObjectId

from app.core.logger import logger
from app.core.exceptions import MessageNotFound, ChatRoomNotFound, InvalidMessageContent
from app.models.message import Message, Offer
from app.schemas.message import MessageSchema
from app.models.conversation import Conversation
from app.services.rabbitmq.producer import publish_message_to_queue
from app.services.rabbitmq.connection import create_rabbitmq_channel
from app.sockets.connection import sio


class MessageDetails:
    """Data class for email message details"""
    def __init__(self, sender: str, amount: str, buyer_username: str, 
                 seller_username: str, title: str, description: str, 
                 delivery_days: str, template: str):
        self.sender = sender
        self.amount = amount
        self.buyer_username = buyer_username
        self.seller_username = seller_username
        self.title = title
        self.description = description
        self.delivery_days = delivery_days
        self.template = template
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "sender": self.sender,
            "amount": self.amount,
            "buyerUsername": self.buyer_username,
            "sellerUsername": self.seller_username,
            "title": self.title,
            "description": self.description,
            "deliveryDays": self.delivery_days,
            "template": self.template
        }


class ChatService:
    """Service class for chat operations"""

    @staticmethod
    async def add_message(data: MessageSchema) -> Message:
        """
        Add a new message to the database and handle related operations.
        Equivalent to the TypeScript addMessage function.
        """
        # Convert schema to model data
        message_data = {
            "conversation_id": data.conversation_id,
            "sender_username": data.sender_username,
            "receiver_username": data.receiver_username,
            "sender_picture": data.sender_picture,
            "receiver_picture": data.receiver_picture,
            "body": data.body or "",
            "file": data.file or "",
            "file_type": data.file_type or "",
            "file_size": data.file_size or "",
            "file_name": data.file_name or "",
            "catalog_id": data.catalog_id or "",
            "buyer_id": data.buyer_id,
            "seller_id": data.seller_id,
            "is_read": getattr(data, 'is_read', False),
            "has_offer": getattr(data, 'has_offer', False),
            "created_at": datetime.utcnow()
        }
        
        # Add offer if present
        if hasattr(data, 'offer') and data.offer:
            offer_data = {
                "catalog_title": getattr(data.offer, 'catalog_title', ''),
                "price": getattr(data.offer, 'price', 0),
                "description": getattr(data.offer, 'description', ''),
                "delivery_in_days": getattr(data.offer, 'delivery_in_days', 0),
                "old_delivery_date": getattr(data.offer, 'old_delivery_date', ''),
                "new_delivery_date": getattr(data.offer, 'new_delivery_date', ''),
                "accepted": getattr(data.offer, 'accepted', False),
                "cancelled": getattr(data.offer, 'cancelled', False)
            }
            offer = Offer(**offer_data)
            message_data["offer"] = offer
        
        # Create the message in database
        message = Message(**message_data)
        await message.create()
        
        logger.info(f"Message created successfully with ID: {message.id}")
        
        # Handle offer email notification
        if getattr(data, 'has_offer', False) and hasattr(data, 'offer') and data.offer:
                email_details = MessageDetails(
                    sender=data.sender_username,
                    amount=str(getattr(data.offer, 'price', 0)),
                    buyer_username=data.receiver_username.lower(),
                    seller_username=data.sender_username.lower(),
                    title=getattr(data.offer, 'catalog_title', ''),
                    description=getattr(data.offer, 'description', ''),
                    delivery_days=str(getattr(data.offer, 'delivery_in_days', 0)),
                    template='offer'
                )
                
                # Send email notification via RabbitMQ
                channel = await create_rabbitmq_channel()
                await publish_message_to_queue(
                    channel=channel,
                    exchange_name="jobber-order-notification",
                    routing_key="order-email",
                    message=email_details.to_dict()
                )
                logger.info("Order email notification sent to notification service.")
        
        # Emit socket message
        # Convert message to dict for socket emission
        message_dict = {
            "id": str(message.id),
            "conversation_id": message.conversation_id,
            "sender_username": message.sender_username,
            "receiver_username": message.receiver_username,
            "sender_picture": message.sender_picture,
            "receiver_picture": message.receiver_picture,
            "body": message.body,
            "file": message.file,
            "file_type": message.file_type,
            "file_size": message.file_size,
            "file_name": message.file_name,
            "catalog_id": message.catalog_id,
            "buyer_id": message.buyer_id,
            "seller_id": message.seller_id,
            "is_read": message.is_read,
            "has_offer": message.has_offer,
            "created_at": message.created_at.isoformat()
        }
        
        if message.offer:
            message_dict["offer"] = {
                "catalog_title": message.offer.catalog_title,
                "price": message.offer.price,
                "description": message.offer.description,
                "delivery_in_days": message.offer.delivery_in_days,
                "old_delivery_date": message.offer.old_delivery_date,
                "new_delivery_date": message.offer.new_delivery_date,
                "accepted": message.offer.accepted,
                "cancelled": message.offer.cancelled
            }
        
        await sio.emit('message received', message_dict)
        logger.info("Socket message emitted successfully")
        return message

    @staticmethod
    async def send_message(message_data: MessageSchema, sender_id: str) -> Message:
        """Send a new message to a chat room"""
        return await ChatService.add_message(message_data)

    @staticmethod
    async def get_conversation(sender_username: str, receiver_username: str) -> Optional[Conversation]:
        """Get conversation between two users"""
        conversation = await Conversation.find_one(
            {
                "$or": [
                    {"sender_username": sender_username, "receiver_username": receiver_username},
                    {"sender_username": receiver_username, "receiver_username": sender_username}
                ]
            }
        )
        return conversation

    @staticmethod
    async def get_user_conversations(username: str) -> List[Conversation]:
        """Get all conversations for a specific user"""
        conversations = await Conversation.find(
            {
                "$or": [
                    {"sender_username": username},
                    {"receiver_username": username}
                ]
            }
        ).to_list()
        return conversations

    @staticmethod
    async def get_messages_between_users(sender_username: str, receiver_username: str) -> List[Message]:
        """Get messages between two users"""
        messages = await Message.find(
            {
                "$or": [
                    {"sender_username": sender_username, "receiver_username": receiver_username},
                    {"sender_username": receiver_username, "receiver_username": sender_username}
                ]
            }
        ).sort("created_at").to_list()
        return messages

    @staticmethod
    async def get_messages_by_conversation(conversation_id: str) -> List[Message]:
        """Get messages by conversation ID"""
        messages = await Message.find(
            {"conversation_id": conversation_id}
        ).sort("created_at").to_list()
        return messages

    @staticmethod
    async def update_offer(offer_data: Dict[str, Any], user_id: str) -> Optional[Message]:
        """Update offer in a message"""
        message_id = offer_data.get("message_id")
        if not message_id:
            raise ValueError("Message ID is required")
        
        message = await Message.get(message_id)
        if not message:
            raise MessageNotFound(f"Message with ID {message_id} not found")
        
        # Update offer fields
        if message.offer:
            for key, value in offer_data.items():
                if hasattr(message.offer, key):
                    setattr(message.offer, key, value)
        
        await message.save()
        return message

    @staticmethod
    async def mark_message_as_read(message_data: Dict[str, Any], user_id: str) -> bool:
        """Mark a single message as read"""
        message_id = message_data.get("message_id")
        if not message_id:
            raise ValueError("Message ID is required")
        
        message = await Message.get(message_id)
        if not message:
            raise MessageNotFound(f"Message with ID {message_id} not found")
        
        message.is_read = True
        await message.save()
        return True

    @staticmethod
    async def mark_multiple_messages_as_read(messages_data: Dict[str, Any], user_id: str) -> bool:
        """Mark multiple messages as read"""
        message_ids = messages_data.get("message_ids", [])
        if not message_ids:
            raise ValueError("Message IDs are required")
        
        # Update multiple messages
        await Message.find(
            {"_id": {"$in": message_ids}}
        ).update({"$set": {"is_read": True}})
        
        return True

    @staticmethod
    async def get_messages(room_id: str, limit: int = 50, offset: int = 0) -> List:
        """Retrieve messages from a chat room with pagination"""
        messages = await Message.find(
            {"conversation_id": room_id}
        ).sort("created_at").skip(offset).limit(limit).to_list()
        return messages

    @staticmethod
    async def handle_notification(message_data: dict) -> None:
        """Handle chat notification from RabbitMQ"""
        logger.info(f"Processing chat notification: {message_data}")
        # Add custom notification handling logic here
        # This could include sending WebSocket notifications, email alerts, etc.