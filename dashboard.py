import time
import requests
import streamlit as st

API = "http://localhost:8000"
STORE_ID = "STORE_BLR_002"

st.set_page_config(
    page_title="Store Intelligence Dashboard",
    layout="wide"
)

st.title("Store Intelligence Dashboard")
st.caption("Live CCTV → Events → Store Analytics")

placeholder = st.empty()

while True:
    try:
        metrics = requests.get(f"{API}/stores/{STORE_ID}/metrics").json()
        funnel = requests.get(f"{API}/stores/{STORE_ID}/funnel").json()
        heatmap = requests.get(f"{API}/stores/{STORE_ID}/heatmap").json()
        anomalies = requests.get(f"{API}/stores/{STORE_ID}/anomalies").json()
        health = requests.get(f"{API}/health").json()

        with placeholder.container():

            st.subheader("Business KPIs")

            c1, c2, c3, c4 = st.columns(4)

            c1.metric("Unique Visitors", metrics.get("unique_visitors", 0))
            c2.metric("Conversion Rate", f'{metrics.get("conversion_rate", 0)}%')
            c3.metric("Revenue", f'₹{metrics.get("revenue_inr", 0)}')
            c4.metric("Transactions", metrics.get("total_transactions", 0))

            st.progress(
                min(metrics.get("conversion_rate", 0) / 100, 1.0),
                text="Conversion Rate"
            )

            st.divider()

            st.subheader("Store Movement")

            m1, m2, m3, m4 = st.columns(4)

            m1.metric("Entries", metrics.get("entry_count", 0))
            m2.metric("Exits", metrics.get("exit_count", 0))
            m3.metric("Staff Detected", metrics.get("staff_events", 0))
            m4.metric("Billing Queue", funnel.get("billing_queue", 0))

            st.divider()

            st.subheader("Conversion Funnel")

            f1, f2, f3, f4 = st.columns(4)

            f1.metric("Entry", funnel.get("entry", 0))
            f2.metric("Zone Visit", funnel.get("zone_visit", 0))
            f3.metric("Billing Queue", funnel.get("billing_queue", 0))
            f4.metric("Dropoff %", f'{funnel.get("dropoff_after_entry_pct", 0)}%')

            st.divider()

            st.subheader("Store Heatmap")

            if heatmap.get("heatmap"):
                for zone in heatmap["heatmap"]:

                    h1, h2, h3 = st.columns(3)

                    h1.metric(
                        zone.get("zone_id", "UNKNOWN"),
                        f'{zone.get("visits", 0)} visits'
                    )

                    h2.metric(
                        "Heat Score",
                        zone.get("heat_score", 0)
                    )

                    h3.metric(
                        "Confidence",
                        zone.get("data_confidence", "UNKNOWN")
                    )
            else:
                st.info("No heatmap data available yet.")

            st.divider()

            st.subheader("System Health")

            for store in health.get("stores", []):

                warning = store.get("warning", "")

                if "STALE" in warning:
                    st.warning(
                        f'{store.get("store_id")} | {warning}'
                    )
                else:
                    st.success(
                        f'{store.get("store_id")} healthy'
                    )

                st.caption(
                    f'Last event: {store.get("last_event_timestamp")}'
                )

            st.divider()

            st.subheader("Anomalies")

            if anomalies.get("anomalies"):

                for anomaly in anomalies["anomalies"]:

                    severity = anomaly.get("severity")
                    anomaly_type = anomaly.get("type")
                    message = anomaly.get("message")
                    action = anomaly.get("suggested_action")

                    if severity == "CRITICAL":
                        st.error(anomaly_type)
                    elif severity == "WARN":
                        st.warning(anomaly_type)
                    else:
                        st.info(anomaly_type)

                    st.write(message)
                    st.caption(f"Suggested action: {action}")

            else:
                st.success("No active anomalies")

    except Exception as e:
        st.error(e)

    time.sleep(5)