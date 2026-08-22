import datetime
from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass

class Portal(Base):
    __tablename__ = "portals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    url: Mapped[str] = mapped_column(String(1024), nullable=False)
    collector_id: Mapped[str] = mapped_column(String(255), nullable=False)
    scraper_type: Mapped[str] = mapped_column(String(50), nullable=False)
    last_run_at: Mapped[datetime.datetime | None] = mapped_column(DateTime(timezone=True))
    health_status: Mapped[str] = mapped_column(String(50), default="unknown")
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    notifications: Mapped[list["Notification"]] = relationship(back_populates="portal")
    heal_events: Mapped[list["HealEvent"]] = relationship(back_populates="portal")
    runs: Mapped[list["Run"]] = relationship(back_populates="portal")

class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    portal_id: Mapped[int] = mapped_column(ForeignKey("portals.id"), nullable=False)
    ext_hash: Mapped[str] = mapped_column(String(64), nullable=False, unique=True, index=True)
    title: Mapped[str] = mapped_column(String(1024), nullable=False)
    posts: Mapped[str | None] = mapped_column(Text)
    vacancies: Mapped[str | None] = mapped_column(Text)
    category: Mapped[str | None] = mapped_column(String(255))
    qualification: Mapped[str | None] = mapped_column(Text)
    state: Mapped[str | None] = mapped_column(String(255))
    apply_start: Mapped[datetime.date | None]
    apply_end: Mapped[datetime.date | None]
    exam_date: Mapped[datetime.date | None]
    pdf_url: Mapped[str | None] = mapped_column(String(2048))
    first_seen_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    portal: Mapped["Portal"] = relationship(back_populates="notifications")
    versions: Mapped[list["NotificationVersion"]] = relationship(back_populates="notification")
    applications: Mapped[list["Application"]] = relationship(back_populates="notification")

class NotificationVersion(Base):
    __tablename__ = "notification_versions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    notification_id: Mapped[int] = mapped_column(
        ForeignKey("notifications.id"), nullable=False
    )
    captured_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    raw_json: Mapped[dict] = mapped_column(JSON, nullable=False)
    diff_summary: Mapped[str | None] = mapped_column(Text)

    notification: Mapped["Notification"] = relationship(back_populates="versions")

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    telegram_id: Mapped[str | None] = mapped_column(String(255), unique=True)
    name: Mapped[str | None] = mapped_column(String(255))
    qualification: Mapped[str | None] = mapped_column(String(255))
    category: Mapped[str | None] = mapped_column(String(255))
    state: Mapped[str | None] = mapped_column(String(255))
    profile_json: Mapped[dict | None] = mapped_column(JSON)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    applications: Mapped[list["Application"]] = relationship(back_populates="user")
    prep_packs: Mapped[list["PrepPack"]] = relationship(back_populates="user")
    mocks: Mapped[list["Mock"]] = relationship(back_populates="user")

class Application(Base):
    __tablename__ = "applications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    notification_id: Mapped[int] = mapped_column(
        ForeignKey("notifications.id"), nullable=False
    )
    status: Mapped[str] = mapped_column(String(50), default="tracking")
    docs_checklist_json: Mapped[dict | None] = mapped_column(JSON)
    applied_at: Mapped[datetime.datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    user: Mapped["User"] = relationship(back_populates="applications")
    notification: Mapped["Notification"] = relationship(back_populates="applications")

class Syllabus(Base):
    __tablename__ = "syllabi"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    exam: Mapped[str] = mapped_column(String(255), nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    captured_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    topics_json: Mapped[dict] = mapped_column(JSON, nullable=False)
    source_url: Mapped[str | None] = mapped_column(String(2048))
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

class SyllabusDiff(Base):
    __tablename__ = "syllabus_diffs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    syllabus_a: Mapped[str] = mapped_column(String(255), nullable=False)
    syllabus_b: Mapped[str] = mapped_column(String(255), nullable=False)
    added_json: Mapped[dict | None] = mapped_column(JSON)
    removed_json: Mapped[dict | None] = mapped_column(JSON)
    summary: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

class PrepPack(Base):
    __tablename__ = "prep_packs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    exam: Mapped[str] = mapped_column(String(255), nullable=False)
    resources_json: Mapped[dict | None] = mapped_column(JSON)
    generated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    user: Mapped["User"] = relationship(back_populates="prep_packs")

class Mock(Base):
    __tablename__ = "mocks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    exam: Mapped[str] = mapped_column(String(255), nullable=False)
    scheduled_for: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    status: Mapped[str] = mapped_column(String(50), default="pending")
    score: Mapped[float | None]
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    user: Mapped["User"] = relationship(back_populates="mocks")

class HealEvent(Base):
    __tablename__ = "heal_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    portal_id: Mapped[int] = mapped_column(ForeignKey("portals.id"), nullable=False)
    detected_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    failure_kind: Mapped[str] = mapped_column(String(255), nullable=False)
    diagnosis: Mapped[str | None] = mapped_column(Text)
    heal_prompt: Mapped[str | None] = mapped_column(Text)
    attempts: Mapped[int] = mapped_column(Integer, default=1)
    resolved: Mapped[bool] = mapped_column(Boolean, default=False)
    duration_s: Mapped[float | None]

    portal: Mapped["Portal"] = relationship(back_populates="heal_events")

class Run(Base):
    __tablename__ = "runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    portal_id: Mapped[int] = mapped_column(ForeignKey("portals.id"), nullable=False)
    started_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    row_count: Mapped[int] = mapped_column(Integer, default=0)
    schema_ok: Mapped[bool] = mapped_column(Boolean, default=True)
    quality_report_json: Mapped[dict | None] = mapped_column(JSON)

    portal: Mapped["Portal"] = relationship(back_populates="runs")