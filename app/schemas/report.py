from pydantic import BaseModel


class ReportStatus(BaseModel):
    found: bool
    report_id: int
    title: str | None = None
    indexing_status: str | None = None
    revision: int | str | None = None