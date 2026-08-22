import time
from src.db.models import HealEvent
from src.scrapers.client import RunResult, ScraperClient
from src.scrapers.quality_gate import QualityReport, check_quality

class HealOrchestrator:
    def __init__(self, max_attempts: int = 3) -> None:
        self.client = ScraperClient()
        self.max_attempts = max_attempts
        self.last_good_snapshot: list[dict] | None = None

    async def run_with_heal(self, collector_id: str, min_rows: int = 1) -> tuple[RunResult, list[HealEvent]]:
        heal_events: list[HealEvent] = []
        start_time = time.monotonic()
        result: RunResult | None = None

        for attempt in range(1, self.max_attempts + 1):
            result = await self.client.run_and_wait(collector_id)
            report = check_quality(result.rows, min_rows, self.last_good_snapshot)

            if report.passed:
                self.last_good_snapshot = result.rows
                return result, heal_events

            prompt = self.heal_prompt(report)
            heal_event = HealEvent(
                portal_id=0,
                detected_at=result,
                failure_kind=report.failure_kind,
                diagnosis=report.diagnosis,
                heal_prompt=prompt,
                attempts=attempt,
                resolved=False,
            )
            heal_events.append(heal_event)

            if attempt < self.max_attempts:
                await self.client.heal(collector_id, prompt)

        duration_s = time.monotonic() - start_time
        for event in heal_events:
            event.duration_s = duration_s

        assert result is not None
        return result, heal_events

    def heal_prompt(self, report: QualityReport) -> str:
        base = f"The scraper is returning bad data. Issue: {report.failure_kind}. {report.diagnosis}"

        if self.last_good_snapshot:
            good_fields = list(self.last_good_snapshot[0].keys()) if self.last_good_snapshot else []
            base += f" Previously working fields were: {good_fields}."

        base += " Please update the scraper selectors to fix this and return data in the same format."
        return base