from coze_coding_dev_sdk.database import Base

from sqlalchemy import Boolean, ForeignKey, Integer, String, Text, DateTime, PrimaryKeyConstraint, func
from sqlalchemy.orm import Mapped, mapped_column
from typing import Optional
import datetime

class HealthCheck(Base):
    __tablename__ = 'health_check'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='health_check_pkey'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True), server_default=func.now(), nullable=True)

# 来访者表
class Visitor(Base):
    __tablename__ = 'visitors'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='visitors_pkey'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[str] = mapped_column(String(100), nullable=False, comment="咨询师ID")
    profile: Mapped[str] = mapped_column(Text, nullable=False, comment="来访者档案/背景")
    disorder_type: Mapped[str] = mapped_column(String(50), nullable=False, comment="症状类型：抑郁/焦虑/PTSD/双相/其他")
    current_phase: Mapped[str] = mapped_column(String(50), default="initial", nullable=False, comment="当前咨询阶段")
    total_sessions: Mapped[int] = mapped_column(Integer, default=0, nullable=False, comment="总咨询次数")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, comment="是否活跃")
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

# 咨询会话表
class ConsultationSession(Base):
    __tablename__ = 'consultation_sessions'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='consultation_sessions_pkey'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    visitor_id: Mapped[int] = mapped_column(Integer, ForeignKey("visitors.id"), nullable=False, comment="来访者ID")
    session_number: Mapped[int] = mapped_column(Integer, nullable=False, comment="第几次咨询")
    status: Mapped[str] = mapped_column(String(20), default="in_progress", nullable=False, comment="状态：in_progress/completed/interrupted")
    start_time: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(timezone=True), nullable=True, comment="开始时间")
    end_time: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(timezone=True), nullable=True, comment="结束时间")
    duration_minutes: Mapped[int] = mapped_column(Integer, default=50, nullable=False, comment="计划时长（分钟）")
    actual_duration_minutes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, comment="实际时长（分钟）")
    departure_type: Mapped[Optional[str]] = mapped_column(String(20), nullable=True, comment="离开类型：ontime/early/delay/abrupt")
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="会话总结")
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

# 对话消息表
class DialogueMessage(Base):
    __tablename__ = 'dialogue_messages'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='dialogue_messages_pkey'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    session_id: Mapped[int] = mapped_column(Integer, ForeignKey("consultation_sessions.id"), nullable=False, comment="会话ID")
    role: Mapped[str] = mapped_column(String(20), nullable=False, comment="角色：counselor/patient")
    content: Mapped[str] = mapped_column(Text, nullable=False, comment="对话内容")
    emotion_state: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, comment="情绪状态")
    counselor_response_type: Mapped[Optional[str]] = mapped_column(String(20), nullable=True, comment="咨询师回应类型：empathy/challenge/support/question")
    message_order: Mapped[int] = mapped_column(Integer, nullable=False, comment="消息序号")
    timestamp: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False, comment="时间戳")
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
