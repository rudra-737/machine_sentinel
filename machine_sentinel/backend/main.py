import json
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from .database import Base, engine, get_db
from . import models, schemas
from .services.risk_engine import evaluate_machine

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Machine Sentinel API",
    version="1.0.0",
    description="Predictive-maintenance portfolio project API",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/machines", response_model=schemas.MachineOut, status_code=status.HTTP_201_CREATED)
def create_machine(payload: schemas.MachineCreate, db: Session = Depends(get_db)):
    machine = models.Machine(**payload.model_dump())
    db.add(machine)
    db.commit()
    db.refresh(machine)
    return machine


@app.get("/machines", response_model=list[schemas.MachineOut])
def list_machines(db: Session = Depends(get_db)):
    return db.query(models.Machine).order_by(models.Machine.id.asc()).all()


def _reading_to_out(reading: models.SensorReading) -> schemas.ReadingOut:
    return schemas.ReadingOut(
        id=reading.id,
        machine_id=reading.machine_id,
        timestamp=reading.timestamp,
        temperature=reading.temperature,
        vibration=reading.vibration,
        current=reading.current,
        rpm=reading.rpm,
        pressure=reading.pressure,
        risk_score=reading.risk_score,
        health_score=reading.health_score,
        state=reading.state,
        reasons=json.loads(reading.reasons_json or "[]"),
    )


@app.post("/readings", response_model=schemas.ReadingOut, status_code=status.HTTP_201_CREATED)
def create_reading(payload: schemas.ReadingCreate, db: Session = Depends(get_db)):
    machine = db.get(models.Machine, payload.machine_id)
    if not machine:
        raise HTTPException(status_code=404, detail="Machine not found")

    evaluation = evaluate_machine(machine, payload)

    reading = models.SensorReading(
        machine_id=payload.machine_id,
        timestamp=payload.timestamp,
        temperature=payload.temperature,
        vibration=payload.vibration,
        current=payload.current,
        rpm=payload.rpm,
        pressure=payload.pressure,
        risk_score=evaluation.risk_score,
        health_score=evaluation.health_score,
        state=evaluation.state,
        reasons_json=json.dumps(evaluation.reasons),
    )
    if reading.timestamp is None:
        from datetime import datetime
        reading.timestamp = datetime.utcnow()

    db.add(reading)
    db.flush()

    if evaluation.state in {"warning", "critical"}:
        severity = "high" if evaluation.state == "critical" else "medium"

        existing = (
            db.query(models.Alert)
            .filter(
                models.Alert.machine_id == machine.id,
                models.Alert.status.in_(["open", "acknowledged"]),
                models.Alert.severity == severity,
            )
            .first()
        )

        if not existing:
            reason_text = ", ".join(evaluation.reasons) or "abnormal operating condition"
            alert = models.Alert(
                machine_id=machine.id,
                reading_id=reading.id,
                severity=severity,
                status="open",
                message=f"{machine.name}: {evaluation.state} condition — {reason_text}",
            )
            db.add(alert)

    db.commit()
    db.refresh(reading)
    return _reading_to_out(reading)


@app.get("/machines/{machine_id}/readings", response_model=list[schemas.ReadingOut])
def recent_readings(
    machine_id: int,
    limit: int = Query(default=50, ge=1, le=500),
    db: Session = Depends(get_db),
):
    if not db.get(models.Machine, machine_id):
        raise HTTPException(status_code=404, detail="Machine not found")

    rows = (
        db.query(models.SensorReading)
        .filter(models.SensorReading.machine_id == machine_id)
        .order_by(models.SensorReading.timestamp.desc())
        .limit(limit)
        .all()
    )
    return [_reading_to_out(row) for row in rows]


@app.get("/machines/{machine_id}/overview")
def machine_overview(machine_id: int, db: Session = Depends(get_db)):
    machine = db.get(models.Machine, machine_id)
    if not machine:
        raise HTTPException(status_code=404, detail="Machine not found")

    latest = (
        db.query(models.SensorReading)
        .filter(models.SensorReading.machine_id == machine_id)
        .order_by(models.SensorReading.timestamp.desc())
        .first()
    )

    open_alerts = (
        db.query(models.Alert)
        .filter(
            models.Alert.machine_id == machine_id,
            models.Alert.status.in_(["open", "acknowledged"]),
        )
        .count()
    )

    return {
        "machine": {
            "id": machine.id,
            "name": machine.name,
            "machine_type": machine.machine_type,
            "location": machine.location,
        },
        "latest_reading": _reading_to_out(latest).model_dump() if latest else None,
        "open_alerts": open_alerts,
    }


@app.get("/alerts", response_model=list[schemas.AlertOut])
def list_alerts(
    status_filter: Optional[str] = Query(default=None, alias="status"),
    severity: Optional[str] = None,
    machine_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    query = db.query(models.Alert)
    if status_filter:
        query = query.filter(models.Alert.status == status_filter)
    if severity:
        query = query.filter(models.Alert.severity == severity)
    if machine_id:
        query = query.filter(models.Alert.machine_id == machine_id)

    return query.order_by(models.Alert.created_at.desc()).all()


@app.patch("/alerts/{alert_id}", response_model=schemas.AlertOut)
def update_alert(alert_id: int, payload: schemas.AlertUpdate, db: Session = Depends(get_db)):
    alert = db.get(models.Alert, alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    alert.status = payload.status
    db.commit()
    db.refresh(alert)
    return alert
