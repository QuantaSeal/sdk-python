"""Compliance resource for generating and retrieving compliance reports."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal

if TYPE_CHECKING:
    from quantaseal._transport import AsyncTransport, SyncTransport

ComplianceFramework = Literal[
    "SOC2",
    "ISO27001",
    "PCI_DSS",
    "HIPAA",
    "GDPR",
    "NIST_CSF",
    "FedRAMP",
    "APRA",
]


class Compliance:
    """Synchronous compliance report generation and retrieval.

    Supported frameworks: SOC2, ISO27001, PCI_DSS, HIPAA, GDPR,
    NIST_CSF, FedRAMP, APRA.

    Usage::

        qs = QuantaSeal(api_key="qs_test_...")

        # Generate a SOC2 report
        job = qs.compliance.generate_report("SOC2")
        report_id = job["report_id"]

        # Poll until ready
        report = qs.compliance.get_report(report_id)

        # Get current compliance score
        score = qs.compliance.get_score("SOC2")
        print(score["score"], score["grade"])
    """

    def __init__(self, transport: SyncTransport) -> None:
        self._transport = transport

    def generate_report(self, framework: ComplianceFramework) -> dict[str, Any]:
        """Trigger generation of a compliance report.

        Args:
            framework: Compliance framework to report against. One of:
                ``SOC2``, ``ISO27001``, ``PCI_DSS``, ``HIPAA``, ``GDPR``,
                ``NIST_CSF``, ``FedRAMP``, ``APRA``.

        Returns:
            Dict with ``report_id``, ``status``, and estimated ``completion_time``.
        """
        resp = self._transport.request(
            "POST",
            "/api/v2/compliance/reports/generate",
            json={"framework": framework},
        )
        return resp.data or {}

    def get_report(self, report_id: str) -> dict[str, Any]:
        """Retrieve a generated compliance report.

        Args:
            report_id: UUID of the report returned by ``generate_report()``.

        Returns:
            Dict with report contents, findings, and ``status`` (``pending`` or ``complete``).

        Raises:
            NotFoundError: If the report does not exist.
        """
        resp = self._transport.request("GET", f"/api/v2/compliance/reports/{report_id}")
        return resp.data or {}

    def list_reports(self) -> list[dict[str, Any]]:
        """List all compliance reports for the tenant.

        Returns:
            List of report metadata dicts (no full contents).
        """
        resp = self._transport.request("GET", "/api/v2/compliance/reports")
        return resp.data or []

    def get_score(self, framework: ComplianceFramework) -> dict[str, Any]:
        """Get the current compliance score for a framework.

        Args:
            framework: Compliance framework to score.

        Returns:
            Dict with ``score`` (0–100), ``grade`` (A–F), ``passed_controls``,
            ``failed_controls``, and ``last_evaluated_at``.
        """
        resp = self._transport.request(
            "GET",
            f"/api/v2/compliance/score",
            params={"framework": framework},
        )
        return resp.data or {}


class AsyncCompliance:
    """Asynchronous compliance operations.

    Same API surface as ``Compliance`` but all methods are ``async``.
    """

    def __init__(self, transport: AsyncTransport) -> None:
        self._transport = transport

    async def generate_report(self, framework: ComplianceFramework) -> dict[str, Any]:
        """Generate a compliance report. See ``Compliance.generate_report`` for details."""
        resp = await self._transport.request(
            "POST",
            "/api/v2/compliance/reports/generate",
            json={"framework": framework},
        )
        return resp.data or {}

    async def get_report(self, report_id: str) -> dict[str, Any]:
        """Retrieve a compliance report. See ``Compliance.get_report`` for details."""
        resp = await self._transport.request(
            "GET", f"/api/v2/compliance/reports/{report_id}"
        )
        return resp.data or {}

    async def list_reports(self) -> list[dict[str, Any]]:
        """List compliance reports. See ``Compliance.list_reports`` for details."""
        resp = await self._transport.request("GET", "/api/v2/compliance/reports")
        return resp.data or []

    async def get_score(self, framework: ComplianceFramework) -> dict[str, Any]:
        """Get compliance score. See ``Compliance.get_score`` for details."""
        resp = await self._transport.request(
            "GET",
            "/api/v2/compliance/score",
            params={"framework": framework},
        )
        return resp.data or {}
