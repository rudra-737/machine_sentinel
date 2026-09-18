from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel, ConfigDict, Field, model_validator


class MachineCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    machine_type: str = Field(min_length=2, max_length=120)
    location: str = Field(min_length=1, max_length=200)
    manufacturer: Optional[str] = None
    model: Optional[str] = None

    temp_warn: float = Field(default=70, gt=0)
    temp_critical: float = Field(default=90, gt=0)
    vibration_warn: float = Field(default=6, gt=0)
    vibration_critical: float = Field(default=10, gt=0)
    current_warn: float = Field(default=14, gt=0)
    current_critical: float = Field(default=20, gt=0)
    rpm_warn: float = Field(default=3200, gt=0)
    rpm_critical: float = Field(default=3600, gt=0)
    pressure_warn: float = Field(default=9, gt=0)
    pressure_critical: float = Field(default=12, gt=0)

    @model_validator(mode="after")
    def validate_threshold_pairs(self):
        pairs = [
            ("temperature", self.temp_warn, self.temp_critical),
            ("vibration", self.vibration_warn, self.vibration_critical),
            ("current", self.current_warn, self.current_critical),
            ("rpm", self.rpm_warn, self.rpm_critical),
            ("pressure", self.pressure_warn, self.pressure_critical),
        ]
        for sensor, warning, critical in pairs:
            if critical < warning:
                raise ValueError(f"{sensor} critical threshold must be >= warning threshold")
        return self


class MachineOut(MachineCreate):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ReadingCreate(BaseModel):
    machine_id: int
    temperature: float = Field(ge=0)
    vibration: float = Field(ge=0)
    current: float = Field(ge=0)
    rpm: float = Field(ge=0)
    pressure: float = Field(ge=0)
    timestamp: Optional[datetime] = None


class ReadingOut(BaseModel):
    id: int
    machine_id: int
    timestamp: datetime
    temperature: float
    vibration: float
    current: float
    rpm: float
    pressure: float
    risk_score: float
    health_score: float
    state: Literal["healthy", "warning", "critical"]
    reasons: list[str]


class AlertUpdate(BaseModel):
    status: Literal["open", "acknowledged", "resolved"]


class AlertOut(BaseModel):
    id: int
    machine_id: int
    reading_id: int
    severity: Literal["medium", "high"]
    status: Literal["open", "acknowledged", "resolved"]
    message: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
