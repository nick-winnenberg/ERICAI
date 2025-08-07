import requests
from bs4 import BeautifulSoup
import streamlit as st

st.sidebar.markdown("### Filters")
query = st.sidebar.text_input("Job Title", "Data Analyst")
location = st.sidebar.text_input("Location", "Remote")
max_results = st.sidebar.slider("Max Results", 10, 100, 30)
source_filter = st.sidebar.multiselect("Source", ["Indeed"], default=["Indeed"])

def scrape_indeed_jobs(query, location, max_results=30):
    jobs = []
    headers = {"User-Agent": "Mozilla/5.0"}
    base_url = "https://www.indeed.com/jobs"

    for start in range(0, max_results, 10):
        params = {"q": query, "l": location, "start": start}
        response = requests.get(base_url, params=params, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")

        for card in soup.select(".job_seen_beacon"):
            try:
                title = card.select_one("h2.jobTitle").text.strip()
                company = card.select_one(".companyName").text.strip()
                loc = card.select_one(".companyLocation").text.strip()
                link = "https://www.indeed.com" + card.select_one("a")["href"]
                jobs.append({"title": title, "company": company, "location": loc, "link": link, "source": "Indeed"})
            except Exception:
                continue

            if len(jobs) >= max_results:
                break
        if len(jobs) >= max_results:
            break

    return jobs

if st.button("Search"):
    with st.spinner("Scraping jobs..."):
        indeed_jobs = scrape_indeed_jobs(query, location)
        # linkedin_jobs = scrape_linkedin_jobs(query, location)
        all_jobs = indeed_jobs  # + linkedin_jobs

        for job in all_jobs:
            st.markdown(f"### [{job['title']}]({job['link']})")
            st.write(f"**Company:** {job['company']}")
            st.write(f"**Location:** {job['location']}")
            st.write(f"**Source:** {job['source']}")
            st.markdown("---")
