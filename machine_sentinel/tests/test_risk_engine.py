from types import SimpleNamespace

from backend.services.risk_engine import evaluate_machine


MACHINE = SimpleNamespace(
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


def reading(temp=50, vibration=3, current=8, rpm=2500, pressure=6):
    return SimpleNamespace(
        temperature=temp,
        vibration=vibration,
        current=current,
        rpm=rpm,
        pressure=pressure,
    )


def test_healthy_reading():
    result = evaluate_machine(MACHINE, reading())
    assert result.state == "healthy"
    assert result.health_score >= 70


def test_warning_reading():
    result = evaluate_machine(MACHINE, reading(temp=75, vibration=6.5))
    assert result.state == "warning"
    assert result.reasons


def test_critical_threshold_forces_critical():
    result = evaluate_machine(MACHINE, reading(vibration=10.5))
    assert result.state == "critical"
    assert any("vibration" in reason for reason in result.reasons)
