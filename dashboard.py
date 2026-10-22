
from pathlib import Path

import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="IBF Advisor Directory",
    page_icon="📊",
    layout="wide",
)

DATA_FILE = Path(__file__).parent / "ibf_advisors.csv"

st.title("IBF Advisor Directory")
st.caption("Interactive directory of advisors listed on ICFS.com")

if not DATA_FILE.exists():
    st.error(f"Dataset not found: {DATA_FILE}")
    st.stop()

df = pd.read_csv(DATA_FILE, dtype=str).fillna("")

expected_columns = [
    "profile_url", "name", "title", "firm", "city",
    "state", "phone", "designations", "member_since", "scraped_by"
]

if list(df.columns) != expected_columns:
    st.error("The CSV columns do not match the required 10-column schema.")
    st.stop()

st.sidebar.header("Filter advisors")
filtered = df.copy()

for column in expected_columns:
    values = sorted(
        value for value in filtered[column].unique()
        if value.strip()
    )
    if not values:
        continue

    selected = st.sidebar.multiselect(
        column.replace("_", " ").title(),
        options=values,
        key=f"filter_{column}",
    )
    if selected:
        filtered = filtered[filtered[column].isin(selected)]

total_count = len(df)
filtered_count = len(filtered)
unique_states = filtered.loc[filtered["state"].ne(""), "state"].nunique()
unique_cities = filtered.loc[filtered["city"].ne(""), "city"].nunique()

st.subheader("Directory Summary")

k1, k2, k3, k4 = st.columns(4)

k1.metric("Total Advisors", f"{total_count:,}")
k2.metric("Filtered Advisors", f"{filtered_count:,}")
k3.metric("Unique State/Region Codes", f"{unique_states:,}")
k4.metric("Unique Cities", f"{unique_cities:,}")

st.caption(
    f"Showing {filtered_count:,} of {total_count:,} advisor records."
)

st.subheader("Filtered Advisor Records")
st.caption(
    "Use the sidebar to filter by any available field. "
    "Select a profile URL in the table and open it in your browser."
)

display_columns = [
    "name", "title", "firm", "city", "state", "phone",
    "designations", "member_since", "profile_url", "scraped_by"
]

st.dataframe(
    filtered[display_columns],
    use_container_width=True,
    hide_index=True,
    height=520,
    column_config={
        "profile_url": st.column_config.LinkColumn("Profile URL"),
    },
)

st.download_button(
    "Download filtered CSV",
    data=filtered[expected_columns].to_csv(index=False).encode("utf-8"),
    file_name="ibf_advisors_filtered.csv",
    mime="text/csv",
)

with st.expander("Data coverage and limitations"):
    st.write(
        "The source listing provides advisor names, profile URLs, "
        "cities, state/region groupings, and IBF designations. "
        "Some cities and state codes are blank where the listing "
        "does not provide a US state/city value."
    )
    st.write(
        "The required submission schema does not contain ZIP code, "
        "website, or email columns. Therefore, ZIP-based and "
        "website/email-based KPIs cannot be calculated from this dataset. "
        "Firm, title, phone, and member-since values remain blank where "
        "they were not available from the accessible source."
    )
