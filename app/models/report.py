"""ORM mappings for the schema supplied in common/sql/schema.sql."""

from datetime import date, datetime

from pgvector.sqlalchemy import VECTOR
from sqlalchemy import BigInteger, Date, ForeignKey, Identity, Integer, Text, TIMESTAMP, VARCHAR, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class ReportCategory(Base):
    __tablename__ = "report_categories"

    category_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    code: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)


class Report(Base):
    __tablename__ = "reports"

    report_id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)
    category_id: Mapped[int] = mapped_column(ForeignKey("report_categories.category_id"), nullable=False)
    overview: Mapped[str] = mapped_column(VARCHAR(1000), nullable=False)
    index_status: Mapped[str] = mapped_column(VARCHAR(20), nullable=False, server_default="pending")
    revision: Mapped[int] = mapped_column(Integer, nullable=False, server_default="1")


class ReportReadView(Base):
    """Read-only mapping of the category-spanning report_read_view."""

    __tablename__ = "report_read_view"

    report_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    category_id: Mapped[int] = mapped_column(Integer, nullable=False)
    category_code: Mapped[str] = mapped_column(Text, nullable=False)
    title: Mapped[str] = mapped_column(VARCHAR(200), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    author: Mapped[str] = mapped_column(VARCHAR(100), nullable=False)
    create_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False)
    update_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False)
    overview: Mapped[str] = mapped_column(VARCHAR(1000), nullable=False)
    index_status: Mapped[str] = mapped_column(VARCHAR(20), nullable=False)
    revision: Mapped[int] = mapped_column(Integer, nullable=False)


class ReportEmbed(Base):
    __tablename__ = "report_embeddings"

    report_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("reports.report_id"), primary_key=True)
    embedding: Mapped[list[float]] = mapped_column(VECTOR(384), nullable=False)
    model_name: Mapped[str] = mapped_column(Text, nullable=False)
    overview_hash: Mapped[str] = mapped_column(VARCHAR(64), nullable=False)
    indexed_revision: Mapped[int] = mapped_column(Integer, nullable=False)
    indexed_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)


class BaseReportBody(Base):
    __abstract__ = True

    report_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("reports.report_id"), primary_key=True)
    title: Mapped[str] = mapped_column(VARCHAR(200), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    author: Mapped[str] = mapped_column(VARCHAR(100), nullable=False)
    create_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    update_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)


class ExperimentReport(BaseReportBody):
    __tablename__ = "experiment_reports"

    experiment_date: Mapped[date] = mapped_column(Date, nullable=False)
    hypothesis: Mapped[str] = mapped_column(Text, nullable=False)
    result_summary: Mapped[str] = mapped_column(Text, nullable=False)


class DailyWorkReport(BaseReportBody):
    __tablename__ = "daily_work_reports"

    work_date: Mapped[date] = mapped_column(Date, nullable=False)
    progress: Mapped[str] = mapped_column(Text, nullable=False)
    blockers: Mapped[str] = mapped_column(Text, nullable=False, server_default="")


class ResearchPlan(BaseReportBody):
    __tablename__ = "research_plans"

    research_goal: Mapped[str] = mapped_column(Text, nullable=False)
    methodology: Mapped[str] = mapped_column(Text, nullable=False)
    target_date: Mapped[date] = mapped_column(Date, nullable=False)


class DataProcessingReport(BaseReportBody):
    __tablename__ = "data_processing_reports"

    dataset_name: Mapped[str] = mapped_column(Text, nullable=False)
    processing_steps: Mapped[str] = mapped_column(Text, nullable=False)
    quality_notes: Mapped[str] = mapped_column(Text, nullable=False, server_default="")


class PromptReport(BaseReportBody):
    __tablename__ = "prompt_reports"

    purpose: Mapped[str] = mapped_column(Text, nullable=False)
    active_version_no: Mapped[int] = mapped_column(Integer, nullable=False, server_default="1")


class PromptVersion(Base):
    __tablename__ = "prompt_versions"

    prompt_version_id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)
    report_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("prompt_reports.report_id"), nullable=False)
    version_no: Mapped[int] = mapped_column(Integer, nullable=False)
    prompt_text: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)


class MeetingMinute(BaseReportBody):
    __tablename__ = "meeting_minutes"

    meeting_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False)
    attendees: Mapped[str] = mapped_column(Text, nullable=False)
    decisions: Mapped[str] = mapped_column(Text, nullable=False)
