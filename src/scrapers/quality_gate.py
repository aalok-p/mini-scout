from pydantic import BaseModel

class QualityReport(BaseModel):
    passed: bool
    failure_kind: str = ""
    diagnosis: str = ""
    details: dict = {}

EXPECTED_FIELDS = {
    "title",
    "posts",
    "vacancies",
    "category",
    "qualification",
    "state",
    "apply_start",
    "apply_end",
    "exam_date",
    "pdf_url",
}

def check_quality(
    rows: list[dict],
    min_rows: int = 1,
    last_good_snapshot: list[dict] | None = None,
) -> QualityReport:
    if not rows or len(rows) < min_rows:
        return QualityReport(
            passed=False,
            failure_kind="empty_or_low_count",
            diagnosis=f"Expected at least {min_rows} rows, got {len(rows)}",
            details={"row_count": len(rows), "threshold": min_rows},
        )

    missing_required = check_fields(rows)
    if missing_required:
        return QualityReport(
            passed=False,
            failure_kind="missing_required_fields",
            diagnosis=f"Required fields missing: {missing_required}",
            details={"missing_fields": list(missing_required)},
        )

    null_report = check_null_rates(rows)
    if null_report:
        return null_report

    if last_good_snapshot:
        drift = check_schema_drift(rows, last_good_snapshot)
        if drift:
            return drift

    return QualityReport(passed=True, details={"row_count": len(rows)})

def check_fields(rows: list[dict]) -> set[str]:
    field_sets = [set(r.keys()) for r in rows]
    if not field_sets:
        return set()

    common_fields = field_sets[0].intersection(*field_sets[1:]) if len(field_sets) > 1 else field_sets[0]
    missing = EXPECTED_FIELDS - common_fields
    return missing

def check_null_rates(rows: list[dict], threshold: float = 0.8) -> QualityReport | None:
    field_nulls: dict[str, int] = {}
    for row in rows:
        for key, value in row.items():
            if value is None or value == "":
                field_nulls[key] = field_nulls.get(key, 0) + 1

    critical = []
    for field, null_count in field_nulls.items():
        rate = null_count / len(rows)
        if rate > threshold:
            critical.append(f"{field} ({rate:.0%} null)")

    if critical:
        return QualityReport(
            passed=False,
            failure_kind="high_null_rate",
            diagnosis=f"Fields with high null rate: {', '.join(critical)}",
            details={"null_fields": critical},
        )

    return None

def check_schema_drift(rows: list[dict], last_good: list[dict]) -> QualityReport | None:
    current_fields = set(rows[0].keys()) if rows else set()
    previous_fields = set(last_good[0].keys()) if last_good else set()

    added = current_fields - previous_fields
    removed = previous_fields - current_fields

    if added or removed:
        return QualityReport(
            passed=False,
            failure_kind="schema_drift",
            diagnosis=f"Schema changed: added={list(added)}, removed={list(removed)}",
            details={"fields_added": list(added), "fields_removed": list(removed)},
        )

    return None