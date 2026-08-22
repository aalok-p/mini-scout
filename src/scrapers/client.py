import asyncio
import json
import subprocess
from dataclasses import dataclass
import httpx
from src.config import config


@dataclass
class RunResult:
    run_id: str
    collector_id: str
    status: str
    rows: list[dict]
    row_count: int


class ScraperClient:
    def __init__(self) -> None:
        self.base_url = "https://api.brightdata.com/dca"
        self.headers = {
            "Authorization": f"Bearer {config.brightdata_api_token}",
            "Content-Type": "application/json",
        }

    async def trigger_run(self, collector_id: str) -> str:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                f"{self.base_url}/trigger",
                headers=self.headers,
                params={"collector_id": collector_id},
            )
            resp.raise_for_status()
            data = resp.json()
            return data["run_id"]

    async def get_run_status(self, run_id: str) -> str:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(
                f"{self.base_url}/run_status",
                headers=self.headers,
                params={"run_id": run_id},
            )
            resp.raise_for_status()
            data = resp.json()
            return data["status"]

    async def get_run_output(self, run_id: str) -> RunResult:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(
                f"{self.base_url}/run_output",
                headers=self.headers,
                params={"run_id": run_id},
            )
            resp.raise_for_status()
            data = resp.json()
            rows = data.get("rows", [])
            return RunResult(
                run_id=run_id,
                collector_id=data.get("collector_id", ""),
                status=data.get("status", "unknown"),
                rows=rows,
                row_count=len(rows),
            )

    async def run_and_wait(self, collector_id: str, poll_interval: float = 5.0, max_wait: float = 300.0) -> RunResult:
        run_id = await self.trigger_run(collector_id)
        elapsed = 0.0

        while elapsed < max_wait:
            status = await self.get_run_status(run_id)
            if status in ("completed", "failed", "error"):
                return await self.get_run_output(run_id)
            await asyncio.sleep(poll_interval)
            elapsed += poll_interval

        raise TimeoutError(f"Run {run_id} did not complete within {max_wait}s")

    async def heal(self, collector_id: str, prompt: str) -> str:
        result = subprocess.run(
            ["npx", "-p", "@brightdata/cli", "bdata", "scraper", "heal", collector_id, prompt],
            capture_output=True,
            text=True,
            timeout=120,
        )
        if result.returncode != 0:
            raise RuntimeError(f"bdata heal failed: {result.stderr}")
        return result.stdout.strip()

    async def create_collector(self, config_data: dict) -> str:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                f"{self.base_url}/create",
                headers=self.headers,
                json=config_data,
            )
            resp.raise_for_status()
            data = resp.json()
            return data["collector_id"]