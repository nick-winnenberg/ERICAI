import streamlit as st
import requests
import pandas as pd

st.title("EricAI API Job Search")

query = st.text_input("Job Title or Keywords", "Warehouse")
location = st.text_input("Location", "Ontario")
num_jobs = 100

def get_jobs_adzuna(query, location, num_jobs):
    url = f"https://api.adzuna.com/v1/api/jobs/us/search/1"
    params = {
        "app_id": "26c021e8",
        "app_key": "0e5d4222db5fef93f52db6fba6a16c6d",
        "results_per_page": num_jobs,
        "what": query,
        "where": location,
        "content-type": "application/json"
    }
    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        jobs = []
        for job in data.get("results", []):
            jobs.append({
                "Title": job.get("title", ""),
                "Company": job.get("company", {}).get("display_name", ""),
                "Location": job.get("location", {}).get("display_name", ""),
                "Summary": job.get("description", "")[:200] + "..." if job.get("description") else "",
                "URL": job.get("redirect_url", ""),
                "Date Posted": job.get("created", "")
            })
        return jobs
    except Exception as e:
        st.error(f"API request failed: {e}")
        return []

if st.button("Search Jobs"):
    with st.spinner("Searching jobs..."):
        jobs = get_jobs_adzuna(query, location, num_jobs)
        if jobs:
            df = pd.DataFrame(jobs)
            st.dataframe(df)
        else:
            st.warning("No jobs found or API request failed.")
