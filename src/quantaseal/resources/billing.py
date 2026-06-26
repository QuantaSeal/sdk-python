"""Billing resource for plan management, usage, and invoices."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from quantaseal._transport import AsyncTransport, SyncTransport


class Billing:
    """Synchronous billing and subscription management operations.

    Usage::

        qs = QuantaSeal(api_key="qs_test_...")

        # Check current plan
        plan = qs.billing.get_plan()
        print(plan["tier"], plan["monthly_price_usd"])

        # View current-period usage
        usage = qs.billing.get_usage()

        # Start upgrade checkout
        session = qs.billing.get_checkout_session("enterprise")
        print(session["checkout_url"])
    """

    def __init__(self, transport: SyncTransport) -> None:
        self._transport = transport

    def get_plan(self) -> dict[str, Any]:
        """Retrieve the current subscription plan.

        Returns:
            Dict with ``tier``, ``monthly_price_usd``, ``features``,
            ``billing_cycle_start``, and ``billing_cycle_end``.
        """
        resp = self._transport.request("GET", "/api/v2/billing/plan")
        return resp.data or {}

    def get_usage(self) -> dict[str, Any]:
        """Retrieve current billing period usage metrics.

        Returns:
            Dict with operation counts by type and aggregate totals for
            the current billing cycle.
        """
        resp = self._transport.request("GET", "/api/v2/billing/usage")
        return resp.data or {}

    def list_invoices(self) -> list[dict[str, Any]]:
        """List all invoices for the tenant.

        Returns:
            List of invoice dicts with ``id``, ``amount_due``, ``status``,
            ``period_start``, ``period_end``, and ``pdf_url``.
        """
        resp = self._transport.request("GET", "/api/v2/billing/invoices")
        return resp.data or []

    def upgrade_plan(self, plan_tier: str) -> dict[str, Any]:
        """Upgrade the subscription plan immediately (for eligible tiers).

        Args:
            plan_tier: Target plan tier (e.g. ``starter``, ``professional``,
                ``enterprise``).

        Returns:
            Dict with the updated ``plan`` and ``effective_date``.
        """
        resp = self._transport.request(
            "POST",
            "/api/v2/billing/upgrade",
            json={"plan_tier": plan_tier},
        )
        return resp.data or {}

    def get_checkout_session(self, plan_tier: str) -> dict[str, Any]:
        """Create a Stripe checkout session for a plan upgrade.

        Args:
            plan_tier: Target plan tier.

        Returns:
            Dict with ``session_id`` and ``checkout_url`` to redirect the user to.
        """
        resp = self._transport.request(
            "POST",
            "/api/v2/billing/checkout",
            json={"plan_tier": plan_tier},
        )
        return resp.data or {}

    def cancel_subscription(self) -> dict[str, Any]:
        """Cancel the current subscription at end of billing period.

        Returns:
            Dict with ``cancelled``, ``effective_date``, and ``access_until`` fields.
        """
        resp = self._transport.request("POST", "/api/v2/billing/cancel")
        return resp.data or {}


class AsyncBilling:
    """Asynchronous billing operations.

    Same API surface as ``Billing`` but all methods are ``async``.
    """

    def __init__(self, transport: AsyncTransport) -> None:
        self._transport = transport

    async def get_plan(self) -> dict[str, Any]:
        """Get current plan. See ``Billing.get_plan`` for details."""
        resp = await self._transport.request("GET", "/api/v2/billing/plan")
        return resp.data or {}

    async def get_usage(self) -> dict[str, Any]:
        """Get current usage. See ``Billing.get_usage`` for details."""
        resp = await self._transport.request("GET", "/api/v2/billing/usage")
        return resp.data or {}

    async def list_invoices(self) -> list[dict[str, Any]]:
        """List invoices. See ``Billing.list_invoices`` for details."""
        resp = await self._transport.request("GET", "/api/v2/billing/invoices")
        return resp.data or []

    async def upgrade_plan(self, plan_tier: str) -> dict[str, Any]:
        """Upgrade the plan. See ``Billing.upgrade_plan`` for details."""
        resp = await self._transport.request(
            "POST",
            "/api/v2/billing/upgrade",
            json={"plan_tier": plan_tier},
        )
        return resp.data or {}

    async def get_checkout_session(self, plan_tier: str) -> dict[str, Any]:
        """Create a checkout session. See ``Billing.get_checkout_session`` for details."""
        resp = await self._transport.request(
            "POST",
            "/api/v2/billing/checkout",
            json={"plan_tier": plan_tier},
        )
        return resp.data or {}

    async def cancel_subscription(self) -> dict[str, Any]:
        """Cancel subscription. See ``Billing.cancel_subscription`` for details."""
        resp = await self._transport.request("POST", "/api/v2/billing/cancel")
        return resp.data or {}
