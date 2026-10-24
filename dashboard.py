
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
    "profile_url",
    "name",
    "title",
    "firm",
    "city",
    "state",
    "phone",
    "designations",
    "member_since",
    "email",
    "scraped_by",
]

# Validate the dataset schema.
missing_columns = [col for col in expected_columns if col not in df.columns]

if missing_columns:
    st.error(
        "The CSV is missing required columns: "
        + ", ".join(missing_columns)
    )
    st.caption(f"Columns found: {df.columns.tolist()}")
    st.stop()

# Keep only the expected columns and maintain a consistent order.
df = df[expected_columns]

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

unique_states = filtered.loc[
    filtered["state"].str.strip().ne(""), "state"
].nunique()

unique_cities = filtered.loc[
    filtered["city"].str.strip().ne(""), "city"
].nunique()

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
    "Open an advisor profile using the Profile URL column."
)

display_columns = [
    "name",
    "title",
    "firm",
    "city",
    "state",
    "phone",
    "designations",
    "member_since",
    "email",
    "profile_url",
    "scraped_by",
]

st.dataframe(
    filtered[display_columns],
    use_container_width=True,
    hide_index=True,
    height=520,
    column_config={
        "name": st.column_config.TextColumn("Name"),
        "title": st.column_config.TextColumn("Title"),
        "firm": st.column_config.TextColumn("Firm"),
        "city": st.column_config.TextColumn("City"),
        "state": st.column_config.TextColumn("State"),
        "phone": st.column_config.TextColumn("Phone"),
        "designations": st.column_config.TextColumn("Designations"),
        "member_since": st.column_config.TextColumn("Member Since"),
        "email": st.column_config.TextColumn("Email"),
        "profile_url": st.column_config.LinkColumn("Profile URL"),
        "scraped_by": st.column_config.TextColumn("Scraped By"),
    },
)

st.download_button(
    "Download filtered CSV",
    data=filtered[expected_columns].to_csv(index=False).encode("utf-8-sig"),
    file_name="ibf_advisors_filtered.csv",
    mime="text/csv",
)

with st.expander("Data coverage and limitations"):
    st.write(
        f"The directory contains {total_count:,} advisor records. "
        "The dataset includes profile URL, name, title, firm, city, "
        "state, phone, designations, member-since year, email, "
        "and scraper attribution."
    )

    st.write(
        "Some title, firm, phone, city, state, and member-since values "
        "are blank in the source data. Blank values are displayed as "
        "empty cells and are not inferred or fabricated."
    )

    st.write(
        "The current IBF dataset does not include ZIP code or website "
        "columns, so ZIP-based and website-based analysis is unavailable."
    )

    st.write(
        "Email values are displayed as provided in the current CSV. "
        "Their presence does not independently establish deliverability."
    )
