from sqlalchemy import text, select

from app.db.session import get_session_factory
from app.core.settings import settings
from app.schemas.report import ReportStatus
from app.models.report import ReportReadView


def get_report_status(report_id: int) -> ReportStatus:
    with get_session_factory()() as conn:
        conn.execute(text(f"SET LOCAL statement_timeout = {int(settings.DB_TIMEOUT_MS)}"))
        row = conn.execute(
            select(
                ReportReadView.report_id,
                ReportReadView.title,
                ReportReadView.index_status,
                ReportReadView.revision,
            ).where(ReportReadView.report_id == report_id)
        ).mappings().first()

    if row is None:
        return ReportStatus(found=False, report_id=report_id)

    return ReportStatus(
        found=True,
        report_id=int(row["report_id"]),
        title=row["title"],
        index_status=str(row["index_status"]),
        revision=row["revision"],
    )