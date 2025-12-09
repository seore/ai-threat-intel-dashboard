import streamlit as st
import pandas as pd
import plotly.express as px

from src.ip_lookup import full_ip_report
from src.feeds import fetch_feodo_blocklist
from src.geo import geocode_ips

st.set_page_config(
    page_title="Threat Intelligence Dashboard",
    layout="wide",
)

st.title("🛡️ Threat Intelligence Dashboard")

st.markdown(
    """
This dashboard lets you:

- 🔍 Look up IP addresses (geo + reputation)  
- 🧪 Browse live malware / botnet IP feeds (Feodo Tracker)  
- 🌍 Visualize malicious activity on a geo heatmap  
"""
)

tabs = st.tabs(["IP Lookup", "Threat Feeds", "Geo Heatmap"])

# IP Lookup
with tabs[0]:
    st.subheader("🔍 IP Lookup")

    ip = st.text_input("Enter IP address", placeholder="8.8.8.8")

    if st.button("Lookup", type="primary") and ip:
        with st.spinner("Querying threat intel sources..."):
            report = full_ip_report(ip)

        st.json(report)

        # Make it pretty if we have geo coords
        lat, lon = report.get("lat"), report.get("lon")
        if lat is not None and lon is not None:
            st.map(pd.DataFrame([{"lat": lat, "lon": lon}]))

# Threat Feeds
with tabs[1]:
    st.subheader("🧪 Feodo Botnet IP Blocklist")

    if st.button("Refresh feed"):
        st.cache_data.clear()

    @st.cache_data(show_spinner=True, ttl=60 * 30)
    def load_feodo():
        return fetch_feodo_blocklist(cache=True)

    df_feodo = load_feodo()

    if df_feodo.empty:
        st.warning("No data returned from Feodo Tracker.")
    else:
        st.write(f"Loaded **{len(df_feodo):,}** suspicious IP entries.")
        st.dataframe(df_feodo.head(200), use_container_width=True)

        col1, col2 = st.columns(2)
        with col1:
            cc = st.text_input("Filter by country (e.g. US, RU, CN)", "")
        with col2:
            asn = st.text_input("Filter by ASN/AS name (contains)", "")

        filtered = df_feodo.copy()
        if cc and "country" in filtered.columns:
            filtered = filtered[filtered["country"].str.upper() == cc.upper()]
        if asn and "asn" in filtered.columns:
            filtered = filtered[filtered["asn"].str.contains(asn, case=False, na=False)]

        st.write(f"Showing **{len(filtered):,}** rows after filters.")
        st.dataframe(filtered.head(500), use_container_width=True)

# Geo Heatmap
with tabs[2]:
    st.subheader("🌍 Geo Heatmap of Malicious IPs")

    st.markdown(
        """
We geolocate IPs from the Feodo blocklist (limited to ~200 for speed)  
and plot them on a map as a density heatmap.
"""
    )

    @st.cache_data(show_spinner=True, ttl=60 * 60)
    def geocode_feodo() -> pd.DataFrame:
        df = fetch_feodo_blocklist(cache=True)
        if df.empty or "ip" not in df.columns:
            return pd.DataFrame()
        return geocode_ips(df["ip"], limit=200)

    if st.button("Generate heatmap"):
        with st.spinner("Geocoding IPs and building map..."):
            geo_df = geocode_feodo()

        if geo_df.empty:
            st.error(
                "Could not geolocate any IPs. "
                "Check your IPINFO_TOKEN or try again later."
            )
        else:
            st.success(f"Geolocated **{len(geo_df):,}** IPs.")
            st.dataframe(
                geo_df[["ip", "city", "region", "country", "org"]].head(50),
                use_container_width=True,
            )

            fig = px.density_mapbox(
                geo_df,
                lat="lat",
                lon="lon",
                z=None,
                hover_name="ip",
                hover_data=["country", "org"],
                radius=15,
                zoom=1,
                height=600,
                mapbox_style="carto-positron",
            )
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Click **Generate heatmap** to build the map.")
