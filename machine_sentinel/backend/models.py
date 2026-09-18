from datetime import datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from .database import Base


class Machine(Base):
    __tablename__ = "machines"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), nullable=False)
    machine_type = Column(String(120), nullable=False)
    location = Column(String(200), nullable=False)
    manufacturer = Column(String(120), nullable=True)
    model = Column(String(120), nullable=True)

    temp_warn = Column(Float, default=70.0, nullable=False)
    temp_critical = Column(Float, default=90.0, nullable=False)
    vibration_warn = Column(Float, default=6.0, nullable=False)
    vibration_critical = Column(Float, default=10.0, nullable=False)
    current_warn = Column(Float, default=14.0, nullable=False)
    current_critical = Column(Float, default=20.0, nullable=False)
    rpm_warn = Column(Float, default=3200.0, nullable=False)
    rpm_critical = Column(Float, default=3600.0, nullable=False)
    pressure_warn = Column(Float, default=9.0, nullable=False)
    pressure_critical = Column(Float, default=12.0, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    readings = relationship("SensorReading", back_populates="machine", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="machine", cascade="all, delete-orphan")


class SensorReading(Base):
    __tablename__ = "sensor_readings"

    id = Column(Integer, primary_key=True, index=True)
    machine_id = Column(Integer, ForeignKey("machines.id"), nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    temperature = Column(Float, nullable=False)
    vibration = Column(Float, nullable=False)
    current = Column(Float, nullable=False)
    rpm = Column(Float, nullable=False)
    pressure = Column(Float, nullable=False)

    risk_score = Column(Float, nullable=False)
    health_score = Column(Float, nullable=False)
    state = Column(String(20), nullable=False, index=True)
    reasons_json = Column(Text, nullable=False, default="[]")

    machine = relationship("Machine", back_populates="readings")


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    machine_id = Column(Integer, ForeignKey("machines.id"), nullable=False, index=True)
    reading_id = Column(Integer, ForeignKey("sensor_readings.id"), nullable=False)

    severity = Column(String(20), nullable=False, index=True)
    status = Column(String(20), nullable=False, default="open", index=True)
    message = Column(String(500), nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    machine = relationship("Machine", back_populates="alerts")
