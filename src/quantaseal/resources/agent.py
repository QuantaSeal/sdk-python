"""Agent resource for AI assistant conversation management."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from quantaseal._transport import AsyncTransport, SyncTransport


class Agent:
    """Synchronous AI agent / assistant operations.

    Usage::

        qs = QuantaSeal(api_key="qs_test_...")

        # Start a new conversation
        response = qs.agent.query("What is my current compliance score?")
        conversation_id = response["conversation_id"]

        # Continue the conversation
        followup = qs.agent.query(
            "How can I improve it?",
            conversation_id=conversation_id,
        )

        # Review past conversations
        conversations = qs.agent.list_conversations()
    """

    def __init__(self, transport: SyncTransport) -> None:
        self._transport = transport

    def query(
        self,
        message: str,
        conversation_id: str | None = None,
    ) -> dict[str, Any]:
        """Send a message to the AI agent.

        Args:
            message: User message / query text.
            conversation_id: Existing conversation UUID for multi-turn dialogue.
                Omit to start a new conversation.

        Returns:
            Dict with ``response``, ``conversation_id``, and optional ``sources``.
        """
        body: dict[str, Any] = {"message": message}
        if conversation_id is not None:
            body["conversation_id"] = conversation_id

        resp = self._transport.request("POST", "/api/v2/agent/query", json=body)
        return resp.data or {}

    def list_conversations(self) -> list[dict[str, Any]]:
        """List all agent conversations for the tenant.

        Returns:
            List of conversation metadata dicts with ``id``, ``title``,
            ``message_count``, and ``last_message_at``.
        """
        resp = self._transport.request("GET", "/api/v2/agent/conversations")
        return resp.data or []

    def get_conversation(self, conversation_id: str) -> dict[str, Any]:
        """Get the full message history for a conversation.

        Args:
            conversation_id: UUID of the conversation to retrieve.

        Returns:
            Dict with ``id``, ``messages`` list, and conversation metadata.

        Raises:
            NotFoundError: If the conversation does not exist.
        """
        resp = self._transport.request(
            "GET", f"/api/v2/agent/conversations/{conversation_id}"
        )
        return resp.data or {}

    def delete_conversation(self, conversation_id: str) -> None:
        """Delete a conversation and all its messages.

        Args:
            conversation_id: UUID of the conversation to delete.

        Raises:
            NotFoundError: If the conversation does not exist.
        """
        self._transport.request_raw(
            "DELETE", f"/api/v2/agent/conversations/{conversation_id}"
        )


class AsyncAgent:
    """Asynchronous agent operations.

    Same API surface as ``Agent`` but all methods are ``async``.
    """

    def __init__(self, transport: AsyncTransport) -> None:
        self._transport = transport

    async def query(
        self,
        message: str,
        conversation_id: str | None = None,
    ) -> dict[str, Any]:
        """Send a message to the agent. See ``Agent.query`` for details."""
        body: dict[str, Any] = {"message": message}
        if conversation_id is not None:
            body["conversation_id"] = conversation_id

        resp = await self._transport.request("POST", "/api/v2/agent/query", json=body)
        return resp.data or {}

    async def list_conversations(self) -> list[dict[str, Any]]:
        """List conversations. See ``Agent.list_conversations`` for details."""
        resp = await self._transport.request("GET", "/api/v2/agent/conversations")
        return resp.data or []

    async def get_conversation(self, conversation_id: str) -> dict[str, Any]:
        """Get a conversation. See ``Agent.get_conversation`` for details."""
        resp = await self._transport.request(
            "GET", f"/api/v2/agent/conversations/{conversation_id}"
        )
        return resp.data or {}

    async def delete_conversation(self, conversation_id: str) -> None:
        """Delete a conversation. See ``Agent.delete_conversation`` for details."""
        await self._transport.request_raw(
            "DELETE", f"/api/v2/agent/conversations/{conversation_id}"
        )
