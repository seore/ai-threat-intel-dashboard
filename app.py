import streamlit as st
import pandas as pd
import plotly.express as px

from src.ip_lookup import full_ip_report
from src.threat_intel.feeds import fetch_feodo_blocklist
from src.geo import geocode_ips

# PAGE CONFIG
st.set_page_config(
    page_title="AI Threat Intelligence Dashboard",
    page_icon="🛰️",
    layout="wide",
)

# CUSTOM CSS
st.markdown(
    """
    <style>
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 3rem;
        max-width: 1200px;
    }

    .app-title {
        font-size: 2.4rem;
        font-weight: 800;
        letter-spacing: 0.08em;
        background: linear-gradient(90deg, #08fdd8, #38bdf8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.25rem;
    }

    .app-subtitle {
        font-size: 0.95rem;
        color: #9ca3af;
        margin-bottom: 1.5rem;
    }

    .card {
        border-radius: 0.9rem;
        padding: 1rem 1.1rem;
        background: radial-gradient(circle at top left, #111827 0, #020617 55%);
        border: 1px solid rgba(148, 163, 184, 0.15);
        box-shadow: 0 18px 45px rgba(15, 23, 42, 0.9);
        margin-bottom: 1rem;
    }

    .card-header {
        font-size: 0.85rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.16em;
        color: #9ca3af;
        margin-bottom: 0.4rem;
    }

    button[role="tab"] {
        text-transform: uppercase;
        letter-spacing: 0.14em;
        font-size: 0.78rem;
    }

    thead tr th {
        background-color: #020617 !important;
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 0.09em;
    }
    tbody tr td {
        font-size: 0.86rem;
    }

    .chip {
        display: inline-flex;
        align-items: center;
        gap: 0.35rem;
        padding: 0.15rem 0.55rem;
        border-radius: 999px;
        background: rgba(15, 23, 42, 0.9);
        border: 1px solid rgba(148, 163, 184, 0.35);
        font-size: 0.7rem;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        color: #9ca3af;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# PAGE HEADER
st.markdown(
    """
    <div>
      <div class="app-title">AI Threat Intelligence Dashboard</div>
      <div class="app-subtitle">
        IP reputation, malware feeds and global geo insights – designed for SOC & blue team workflows.
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# PAGE SIDEBAR
st.sidebar.markdown("### ⚙️ View Controls")
st.sidebar.markdown(
    "- Use **IP Lookup** for single host enrichment\n"
    "- **Threat Feeds** shows live botnet / C2 IPs\n"
    "- **Geo Heatmap** reveals global distribution"
)


# CACHED HELPERS
@st.cache_data(show_spinner=True, ttl=60 * 30)
def load_feodo():
    """Fetch & cache Feodo Tracker blocklist."""
    return fetch_feodo_blocklist(cache=True)


@st.cache_data(show_spinner=True, ttl=60 * 60)
def geocode_feodo(limit: int = 200) -> pd.DataFrame:
    """Geolocate a subset of Feodo IPs for mapping."""
    df = fetch_feodo_blocklist(cache=True)
    if df.empty or "ip" not in df.columns:
        return pd.DataFrame()
    return geocode_ips(df["ip"], limit=limit)


# MAIN INTRO CARD
st.markdown(
    """
    <div class="card">
      <div class="card-header">Overview</div>
      <div>
        This dashboard lets you:
        <ul>
          <li>Enrich IPs with geo & reputation</li>
          <li>Inspect live Feodo botnet / C2 IP feeds</li>
          <li>Visualise malicious activity on an interactive geo heatmap</li>
        </ul>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

tabs = st.tabs(["IP Lookup", "Threat Feeds", "Geo Heatmap"])

# IP Lookup
with tabs[0]:
    left, right = st.columns([1.2, 1])

    with left:
        st.markdown(
            """
            <div class="card">
              <div class="card-header">IP Lookup</div>
              <p>Run an on-demand enrichment for a single IP address using your configured intel sources.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        ip = st.text_input("IP address", placeholder="8.8.8.8")

        lookup_clicked = st.button("Lookup", type="primary")

        if lookup_clicked and ip:
            with st.spinner("Querying threat intel sources..."):
                report = full_ip_report(ip)

            st.markdown(
                f"""
                <div class="chip" style="margin-top: 0.3rem; margin-bottom: 0.4rem;">
                  IP REPORT • {ip}
                </div>
                """,
                unsafe_allow_html=True,
            )

            st.json(report)

    with right:
        st.markdown(
            """
            <div class="card">
              <div class="card-header">Geo Location</div>
              <p>When geo data is available, the IP is plotted below.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if "report" in locals():
            lat, lon = report.get("lat"), report.get("lon")
            if lat is not None and lon is not None:
                st.map(pd.DataFrame([{"lat": lat, "lon": lon}]))
            else:
                st.info("No latitude/longitude available for this IP.")
        else:
            st.info("Run a lookup to see geo information here.")


# Threat Feeds
with tabs[1]:
    st.markdown(
        """
        <div class="card">
          <div class="card-header">Feodo Botnet IP Blocklist</div>
          <p>
            Live feed of botnet / C2 IPs from Feodo Tracker. Use filters to pivot by country and ASN.
          </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    top_row = st.columns([0.25, 0.75])
    with top_row[0]:
        if st.button("🔄 Refresh feed"):
            st.cache_data.clear()

    df_feodo = load_feodo()

    if df_feodo.empty:
        st.warning("No data returned from Feodo Tracker.")
    else:
        total = len(df_feodo)
        countries = (
            df_feodo["country"].nunique() if "country" in df_feodo.columns else 0
        )

        kpi1, kpi2 = st.columns(2)
        kpi1.metric("Suspicious IP entries", f"{total:,}")
        kpi2.metric("Countries observed", countries)

        st.dataframe(df_feodo.head(200), use_container_width=True, hide_index=True)

        st.markdown("#### Filters")

        col1, col2 = st.columns(2)
        with col1:
            cc = st.text_input("Filter by country (e.g. US, RU, CN)", "")
        with col2:
            asn = st.text_input("Filter by ASN / AS name (contains)", "")

        filtered = df_feodo.copy()
        if cc and "country" in filtered.columns:
            filtered = filtered[filtered["country"].str.upper() == cc.upper()]
        if asn and "asn" in filtered.columns:
            filtered = filtered[filtered["asn"].str.contains(asn, case=False, na=False)]

        st.write(f"Showing **{len(filtered):,}** rows after filters.")
        st.dataframe(filtered.head(500), use_container_width=True, hide_index=True)


# Geo Heatmap
with tabs[2]:
    st.markdown(
        """
        <div class="card">
          <div class="card-header">Global View</div>
          <p>
            We geolocate a subset of Feodo IPs (limited for speed) and display them on a density heatmap.
            This highlights hotspots of botnet / C2 infrastructure.
          </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col_limit, _ = st.columns([0.35, 0.65])
    with col_limit:
        limit = st.slider(
            "Max IPs to geolocate",
            min_value=50,
            max_value=500,
            value=200,
            step=50,
            help="Higher values give richer maps but may be slower.",
        )

    if st.button("Generate heatmap"):
        with st.spinner("Geocoding IPs and building map..."):
            geo_df = geocode_feodo(limit=limit)

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
                hide_index=True,
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
        st.info("Set a limit and click **Generate heatmap** to build the map.")
