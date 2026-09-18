from dataclasses import dataclass


@dataclass
class Evaluation:
    risk_score: float
    health_score: float
    state: str
    reasons: list[str]


def _sensor_risk(value: float, warning: float, critical: float) -> tuple[float, str | None, bool]:
    if value >= critical:
        return 100.0, "critical limit exceeded", True

    ratio = value / warning if warning > 0 else 0.0

    if ratio < 0.80:
        return max(0.0, ratio * 20.0), None, False
    if ratio < 1.0:
        # 16..35 as it approaches warning
        return 16.0 + ((ratio - 0.80) / 0.20) * 19.0, "approaching warning limit", False

    # warning to critical: 40..95
    span = max(critical - warning, 1e-9)
    position = min(1.0, (value - warning) / span)
    return 40.0 + position * 55.0, "above warning limit", False


def evaluate_machine(machine, reading) -> Evaluation:
    sensors = {
        "temperature": (reading.temperature, machine.temp_warn, machine.temp_critical),
        "vibration": (reading.vibration, machine.vibration_warn, machine.vibration_critical),
        "current": (reading.current, machine.current_warn, machine.current_critical),
        "rpm": (reading.rpm, machine.rpm_warn, machine.rpm_critical),
        "pressure": (reading.pressure, machine.pressure_warn, machine.pressure_critical),
    }

    risks: list[float] = []
    reasons: list[str] = []
    critical_hit = False

    for name, (value, warning, critical) in sensors.items():
        sensor_risk, reason, sensor_critical = _sensor_risk(value, warning, critical)
        risks.append(sensor_risk)
        critical_hit = critical_hit or sensor_critical

        if reason:
            reasons.append(f"{name} {reason}")

    max_risk = max(risks)
    avg_risk = sum(risks) / len(risks)

    # Bias toward the worst sensor while keeping multi-sensor deterioration visible.
    risk_score = round(min(100.0, 0.7 * max_risk + 0.3 * avg_risk), 1)
    health_score = round(max(0.0, 100.0 - risk_score), 1)

    if critical_hit or health_score < 40:
        state = "critical"
    elif health_score < 70:
        state = "warning"
    else:
        state = "healthy"

    return Evaluation(
        risk_score=risk_score,
        health_score=health_score,
        state=state,
        reasons=reasons,
    )
