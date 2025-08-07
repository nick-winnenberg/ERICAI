import time
import requests
from bs4 import BeautifulSoup
import streamlit as st

# Sidebar UI
st.sidebar.markdown("### Filters")
query = st.sidebar.text_input("Job Title", "Data Analyst")
location = st.sidebar.text_input("Location", "Remote")
max_results = st.sidebar.slider("Max Results", 10, 100, 30)
source_filter = st.sidebar.multiselect("Source", ["Indeed"], default=["Indeed"])

# Function to scrape jobs from Indeed
def scrape_indeed_jobs(query, location, max_results=30):
    jobs = []
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/115.0 Safari/537.36"
        ),
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.indeed.com/"
    }
    base_url = "https://www.indeed.com/jobs"

    for start in range(0, max_results, 10):
        params = {"q": query, "l": location, "start": start}
        response = requests.get(base_url, params=params, headers=headers)

        if response.status_code != 200:
            st.error(f"Request failed with status code {response.status_code}")
            break

        soup = BeautifulSoup(response.text, "html.parser")
        job_cards = soup.select(".job_seen_beacon")

        for card in job_cards:
            try:
                title_elem = card.select_one("h2.jobTitle")
                company_elem = card.select_one(".companyName")
                location_elem = card.select_one(".companyLocation")
                link_elem = card.select_one("a")

                title = title_elem.text.strip() if title_elem else "N/A"
                company = company_elem.text.strip() if company_elem else "N/A"
                loc = location_elem.text.strip() if location_elem else "N/A"
                link = "https://www.indeed.com" + link_elem["href"] if link_elem else "#"

                jobs.append({
                    "title": title,
                    "company": company,
                    "location": loc,
                    "link": link,
                    "source": "Indeed"
                })
            except Exception as e:
                continue  # Optionally: log the error with st.warning(str(e))

            if len(jobs) >= max_results:
                break

        if len(jobs) >= max_results:
            break

        time.sleep(1)  # Be polite and avoid being blocked

        st.code(soup.prettify()[:2000], language="html")

    return jobs

# Cache the scraper for performance
@st.cache_data(ttl=600)
def get_indeed_jobs(query, location, max_results):
    return scrape_indeed_jobs(query, location, max_results)

# Main interface
if st.button("Search"):
    with st.spinner("Scraping jobs from Indeed..."):
        all_jobs = []

        if "Indeed" in source_filter:
            indeed_jobs = get_indeed_jobs(query, location, max_results)
            all_jobs.extend(indeed_jobs)

        if not all_jobs:
            st.warning("No jobs found. Try adjusting your filters.")
        else:
            for job in all_jobs:
                st.markdown(f"### [{job['title']}]({job['link']})")
                st.write(f"**Company:** {job['company']}")
                st.write(f"**Location:** {job['location']}")
                st.write(f"**Source:** {job['source']}")
                st.markdown("---")
