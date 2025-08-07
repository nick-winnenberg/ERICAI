import streamlit as st
from playwright.sync_api import sync_playwright

def scrape_indeed_with_playwright(query="Data Analyst", location="Remote", max_results=30):
    jobs = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        url = f"https://www.indeed.com/jobs?q={query}&l={location}"
        st.write(f"Visiting: {url}")
        try:
            page.goto(url, timeout=60000)
            page.wait_for_selector(".job_seen_beacon", timeout=15000)

            job_cards = page.locator(".job_seen_beacon")
            count = job_cards.count()

            for i in range(min(count, max_results)):
                card = job_cards.nth(i)
                try:
                    title = card.locator("h2.jobTitle").inner_text(timeout=5000)
                    company = card.locator(".companyName").inner_text(timeout=5000)
                    loc = card.locator(".companyLocation").inner_text(timeout=5000)
                    link = card.locator("a").get_attribute("href")
                    full_link = f"https://www.indeed.com{link}" if link else "#"

                    jobs.append({
                        "title": title,
                        "company": company,
                        "location": loc,
                        "link": full_link,
                        "source": "Indeed"
                    })
                except Exception as card_err:
                    st.warning(f"Job skipped due to: {card_err}")
                    continue
        except Exception as page_err:
            st.error("Failed to load or parse the page:")
            st.code(traceback.format_exc())
        finally:
            browser.close()
    return jobs