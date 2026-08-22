from pathlib import Path
import yaml
from pydantic import BaseModel


class CollectorConfig(BaseModel):
    name: str
    url: str
    collector_id: str
    scraper_type: str
    schedule: str
    quality_threshold: int

def load_collectors(path: Path | None = None) -> list[CollectorConfig]:
    if path is None:
        path = Path("collectors.yaml")

    with open(path) as f:
        data = yaml.safe_load(f)

    return [CollectorConfig(**item) for item in data["portals"]]

def get_collector_by_name(name: str) -> CollectorConfig | None:
    collectors = load_collectors()
    for c in collectors:
        if c.name == name:
            return c
    return None

def get_collector_by_id(collector_id: str) -> CollectorConfig | None:
    collectors = load_collectors()
    for c in collectors:
        if c.collector_id == collector_id:
            return c
    return None