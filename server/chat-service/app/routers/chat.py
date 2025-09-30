"""
Chat router for handling chat-related endpoints.
"""
from fastapi import APIRouter, status, HTTPException, Depends, Body
from fastapi.responses import JSONResponse
from typing import List, Optional

from app.core.logger import logger
from app.core.constants import SERVICE_NAME
from app.services.chat_service import ChatService
from app.schemas.message import MessageSchema
from server_shared.middlewares.auth_dependency import get_current_user

router = APIRouter()


@router.get(
    "/conversation/{sender_username}/{receiver_username}",
    status_code=status.HTTP_200_OK,
    response_description="Get conversation between two users",
    tags=["Chat"],
    operation_id="get_conversation_v1"
)
async def conversation(
    sender_username: str,
    receiver_username: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get conversation between two users.
    """
    logger.info(f"{SERVICE_NAME}: conversation() called for {sender_username} and {receiver_username}")
    conversation = await ChatService.get_conversation(sender_username, receiver_username)
    return conversation


@router.get(
    "/conversations/{username}",
    status_code=status.HTTP_200_OK,
    response_description="Get all conversations for a user",
    tags=["Chat"],
    operation_id="get_conversation_list_v1"
)
async def conversation_list(
    username: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get all conversations for a specific user.
    """
    logger.info(f"{SERVICE_NAME}: conversation_list() called for {username}")
    conversations = await ChatService.get_user_conversations(username)
    return conversations


@router.get(
    "/{sender_username}/{receiver_username}",
    status_code=status.HTTP_200_OK,
    response_description="Get messages between two users",
    tags=["Chat"],
    operation_id="get_messages_v1"
)
async def messages(
    sender_username: str,
    receiver_username: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get messages between two users.
    """
    logger.info(f"{SERVICE_NAME}: messages() called for {sender_username} and {receiver_username}")
    messages = await ChatService.get_messages_between_users(sender_username, receiver_username)
    return messages


@router.get(
    "/{conversation_id}",
    status_code=status.HTTP_200_OK,
    response_description="Get messages by conversation ID",
    tags=["Chat"],
    operation_id="get_user_messages_v1"
)
async def user_messages(
    conversation_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get messages by conversation ID.
    """
    logger.info(f"{SERVICE_NAME}: user_messages() called for conversation {conversation_id}")
    messages = await ChatService.get_messages_by_conversation(conversation_id)
    return messages


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_description="Send a message",
    tags=["Chat"],
    operation_id="send_message_v1"
)
async def message(
    message_data: MessageSchema,
    current_user: dict = Depends(get_current_user)
):
    """
    Send a new message.
    """
    logger.info(f"{SERVICE_NAME}: message() called")
    message = await ChatService.send_message(message_data, current_user["user_id"])
    return message


@router.put(
    "/offer",
    status_code=status.HTTP_200_OK,
    response_description="Update message offer",
    tags=["Chat"],
    operation_id="update_offer_v1"
)
async def offer(
    offer_data: dict = Body(...),
    current_user: dict = Depends(get_current_user)
):
    """
    Update offer in a message.
    """
    logger.info(f"{SERVICE_NAME}: offer() called")
    updated_message = await ChatService.update_offer(offer_data, current_user["user_id"])
    return updated_message


@router.put(
    "/mark-as-read",
    status_code=status.HTTP_200_OK,
    response_description="Mark single message as read",
    tags=["Chat"],
    operation_id="mark_single_message_read_v1"
)
async def mark_single_message(
    message_data: dict = Body(...),
    current_user: dict = Depends(get_current_user)
):
    """
    Mark a single message as read.
    """
    logger.info(f"{SERVICE_NAME}: mark_single_message() called")
    result = await ChatService.mark_message_as_read(message_data, current_user["user_id"])
    return result


@router.put(
    "/mark-multiple-as-read",
    status_code=status.HTTP_200_OK,
    response_description="Mark multiple messages as read",
    tags=["Chat"],
    operation_id="mark_multiple_messages_read_v1"
)
async def mark_multiple_messages(
    messages_data: dict = Body(...),
    current_user: dict = Depends(get_current_user)
):
    """
    Mark multiple messages as read.
    """
    logger.info(f"{SERVICE_NAME}: mark_multiple_messages() called")
    result = await ChatService.mark_multiple_messages_as_read(messages_data, current_user["user_id"])
    return result
