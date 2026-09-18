from .database import Base, SessionLocal, engine
from .models import Machine

Base.metadata.create_all(bind=engine)

db = SessionLocal()
try:
    if db.query(Machine).count() == 0:
        db.add(
            Machine(
                name="Pump P-101",
                machine_type="centrifugal_pump",
                location="Demo Plant - Bay 1",
                manufacturer="DemoCorp",
                model="CP-10",
                temp_warn=70,
                temp_critical=90,
                vibration_warn=6,
                vibration_critical=10,
                current_warn=14,
                current_critical=20,
                rpm_warn=3200,
                rpm_critical=3600,
                pressure_warn=9,
                pressure_critical=12,
            )
        )
        db.commit()
        print("Seeded demo machine.")
    else:
        print("Database already contains machines.")
finally:
    db.close()
