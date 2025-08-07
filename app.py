import streamlit as st
import requests
import pandas as pd

# --- Page Setup ---
st.set_page_config(page_title="Findwork Job Board", layout="wide")
st.title("💼 Tech Job Board (via Findwork API)")

# --- Sidebar Filters ---
st.sidebar.header("Search Filters")
search_query = st.sidebar.text_input("Keyword", value="data")
location = st.sidebar.text_input("Location (optional)", value="")
limit = st.sidebar.slider("Max Results", min_value=10, max_value=50, step=10)

# --- API Call ---
def fetch_jobs(query, location, limit):
    url = "https://findwork.dev/api/jobs/"
    params = {"search": query}
    response = requests.get(url, params=params)
    data = response.json()

    jobs = []
    for job in data.get("results", [])[:limit]:
        if location and location.lower() not in job["location"].lower():
            continue
        jobs.append({
            "Title": job["role"],
            "Company": job["company_name"],
            "Location": job["location"],
            "Date Posted": job["date_posted"],
            "Job Type": job["employment_type"],
            "Remote": job["remote"],
            "Link": job["url"]
        })

    return pd.DataFrame(jobs)

# --- Main App ---
if st.button("🔍 Search Jobs"):
    with st.spinner("Fetching jobs..."):
        df = fetch_jobs(search_query, location, limit)
        if not df.empty:
            st.success(f"Found {len(df)} jobs!")
            st.dataframe(df)
        else:
            st.warning("No jobs found. Try a broader keyword or remove location filter.")
