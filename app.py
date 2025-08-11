import streamlit as st
import requests
import pandas as pd
from googlesearch import search

rapidapi_key = "dc65875df5mshd34e66296c6af73p1ba678jsnf3d228245e9d"
adzuna_key = "0e5d4222db5fef93f52db6fba6a16c6d"

st.title("EricAI API Job Search")

query = st.text_input("Job Title or Keywords", "Warehouse")
location = st.text_input("Location", "Ontario")
num_jobs = 100

def get_jobs_adzuna(query, location, num_jobs):
    url = f"https://api.adzuna.com/v1/api/jobs/us/search/1"
    params = {
        "app_id": "26c021e8",
        "app_key": adzuna_key,
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
        st.error(f"Adzuna API request failed: {e}")
        return []

def get_jobs_google(query, location, num_jobs):
    search_query = f"{query} jobs in {location}"
    jobs = []
    try:
        for url in search(search_query, num_results=num_jobs, lang="en"):
            jobs.append({
                "Title": query,
                "Location": location,
                "URL": url,
            })
        return jobs
    except Exception as e:
        st.error(f"Google search failed: {e}")
        return []

def get_jobs_jsearch(query, location, num_jobs):
    url = "https://jsearch.p.rapidapi.com/search"
    headers = {
        "X-RapidAPI-Key": rapidapi_key,  # Replace with your RapidAPI key
        "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
    }
    params = {
        "query": f"{query} in {location}",
        "num_pages": 1
    }
    jobs = []
    try:
        resp = requests.get(url, headers=headers, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        for job in data.get("data", [])[:num_jobs]:
            jobs.append({
                "Title": job.get("job_title", ""),
                "Company": job.get("employer_name", ""),
                "Location": job.get("job_city", ""),
                "Summary": job.get("job_description", "")[:200] + "..." if job.get("job_description") else "",
                "URL": job.get("job_apply_link", ""),
                "Date Posted": job.get("job_posted_at_datetime_utc", "")
            })
        return jobs
    except Exception as e:
        st.error(f"JSearch API request failed: {e}")
        return []

sources = st.multiselect(
    "Job Sources",
    ["Adzuna", "Google Jobs", "JSearch"],
    default=["Adzuna"]
)

if st.button("Search Jobs"):
    with st.spinner("Searching jobs..."):
        all_jobs = []
        google_links = []
        if "Adzuna" in sources:
            all_jobs.extend(get_jobs_adzuna(query, location, num_jobs))
        if "Google Jobs" in sources:
            google_links.extend(get_jobs_google(query, location, num_jobs))
        if "JSearch" in sources:
            all_jobs.extend(get_jobs_jsearch(query, location, num_jobs))

        if all_jobs:
            df = pd.DataFrame(all_jobs)
            st.subheader("Job Listings")
            st.write(f"Found {len(df)} jobs.")
            st.dataframe(df)

        if google_links:
            st.subheader("Google Job Links")
            google_df = pd.DataFrame(google_links)
            # Extract domain name between first two periods
            def extract_domain(url):
                try:
                    domain = url.split("//")[-1].split("/")[0]
                    parts = domain.split(".")
                    if len(parts) >= 3:
                        return parts[1]
                    elif len(parts) == 2:
                        return parts[0]
                    else:
                        return domain
                except Exception:
                    return ""
            if not google_df.empty and "URL" in google_df.columns:
                google_df["Domain"] = google_df["URL"].apply(extract_domain)
                google_df["URL"] = google_df["URL"].apply(lambda x: f'<a href="{x}" target="_blank">{x}</a>')
                st.write(google_df.to_html(escape=False, index=False), unsafe_allow_html=True)
            else:
                st.dataframe(google_df)





        else:
            st.warning("No jobs found or API request failed.")
