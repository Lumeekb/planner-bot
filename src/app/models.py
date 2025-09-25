from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import BigInteger, String, Text, Date, Boolean, JSON, Integer
import datetime as dt
from .db import Base

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tg_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    locale: Mapped[str] = mapped_column(String(8), default="ru")
    tz: Mapped[str] = mapped_column(String(64), default="Europe/Helsinki")
    morning_time: Mapped[str] = mapped_column(String(8), default="09:15")
    evening_time: Mapped[str] = mapped_column(String(8), default="21:30")
    plan: Mapped[str] = mapped_column(String(16), default="free")

class MIT(Base):
    __tablename__ = "mits"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(index=True)
    for_date: Mapped[dt.date] = mapped_column(Date, default=dt.date.today)
    cat: Mapped[str] = mapped_column(String(32))   # A/B/C или своя категория
    title: Mapped[str] = mapped_column(Text)
    dod: Mapped[str] = mapped_column(Text, default="")
    next_step: Mapped[str] = mapped_column(Text, default="")
    done: Mapped[bool] = mapped_column(default=False)

class Review(Base):
    __tablename__ = "reviews"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(index=True)
    for_date: Mapped[dt.date] = mapped_column(Date, default=dt.date.today)
    wins: Mapped[JSON] = mapped_column(JSON, default=list)
    blockers: Mapped[str] = mapped_column(Text, default="")
    lessons: Mapped[str] = mapped_column(Text, default="")

class HorizonTask(Base):
    """
    Задачи по горизонту: 'month' или 'week'.
    anchor_date: для месяца — первый день месяца; для недели — понедельник ISO.
    """
    __tablename__ = "horizon_tasks"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(index=True)
    horizon: Mapped[str] = mapped_column(String(10))  # 'month' | 'week'
    anchor_date: Mapped[dt.date] = mapped_column(Date)
    title: Mapped[str] = mapped_column(Text)
    done: Mapped[bool] = mapped_column(default=False)
    notes: Mapped[str] = mapped_column(Text, default="")

class Subtask(Base):
    """Подзадачи к дневным MIT (связь по mit_id)."""
    __tablename__ = "subtasks"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(index=True)
    mit_id: Mapped[int] = mapped_column(Integer, index=True)  # ссылку делаем без FK для простоты
    title: Mapped[str] = mapped_column(Text)
    done: Mapped[bool] = mapped_column(default=False)
	
