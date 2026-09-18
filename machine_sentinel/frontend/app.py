import os
import pandas as pd
import requests
import streamlit as st

API_URL = os.getenv(
    "API_URL",
    "https://machine-sentinel.onrender.com"
).rstrip("/")

st.set_page_config(page_title="Machine Sentinel", layout="wide")
st.title("Machine Sentinel")
st.caption("Predictive maintenance & fault detection dashboard")

try:
    machines = requests.get(f"{API_URL}/machines", timeout=5).json()
except Exception as exc:
    st.error(f"Cannot reach API at {API_URL}. Start FastAPI first. Details: {exc}")
    st.stop()

if not machines:
    st.info("No machines found. Create one in FastAPI Swagger at /docs or run the seed script.")
    st.stop()

machine_labels = {f"{m['name']} — {m['location']}": m["id"] for m in machines}
selected_label = st.selectbox("Machine", list(machine_labels.keys()))
machine_id = machine_labels[selected_label]

overview = requests.get(f"{API_URL}/machines/{machine_id}/overview", timeout=5).json()
latest = overview.get("latest_reading")

c1, c2, c3 = st.columns(3)
if latest:
    c1.metric("Health Score", f"{latest['health_score']}/100")
    c2.metric("State", latest["state"].upper())
    c3.metric("Open Alerts", overview["open_alerts"])

    st.subheader("Latest Measurements")
    values = {
        "Temperature (°C)": latest["temperature"],
        "Vibration (mm/s)": latest["vibration"],
        "Current (A)": latest["current"],
        "RPM": latest["rpm"],
        "Pressure (bar)": latest["pressure"],
    }
    st.dataframe(pd.DataFrame([values]), use_container_width=True)
else:
    st.warning("No readings available for this machine.")

st.subheader("Recent Telemetry")
readings = requests.get(
    f"{API_URL}/machines/{machine_id}/readings",
    params={"limit": 100},
    timeout=5,
).json()

if readings:
    df = pd.DataFrame(readings)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    st.line_chart(
        df.set_index("timestamp")[["temperature", "vibration", "current", "pressure"]]
    )
    st.dataframe(
        df[["timestamp", "health_score", "risk_score", "state"]].sort_values(
            "timestamp", ascending=False
        ),
        use_container_width=True,
    )
else:
    st.info("No telemetry yet.")

st.subheader("Active Alerts")
alerts = requests.get(
    f"{API_URL}/alerts",
    params={"machine_id": machine_id},
    timeout=5,
).json()
active = [a for a in alerts if a["status"] != "resolved"]
if active:
    st.dataframe(pd.DataFrame(active), use_container_width=True)
else:
    st.success("No active alerts.")
