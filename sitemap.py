import streamlit as st
import requests
from datetime import datetime
from bs4 import BeautifulSoup
import csv

# Function to extract the domain name from the URL
def extract_domain(url):
    return url.split('//')[-1].split('/')[0]

# Function to process XML sitemaps
def process_sitemap(url, user_agent, csv_writer):
    response = requests.get(url, headers={'User-Agent': user_agent})
    soup = BeautifulSoup(response.content, 'xml')
    for loc in soup.find_all('loc'):
        url = loc.text
        response = requests.head(url, headers={'User-Agent': user_agent})
        response_code = response.status_code
        if response_code == 200:
            page_response = requests.get(url, headers={'User-Agent': user_agent})
            page_content = page_response.content
            soup = BeautifulSoup(page_content, 'html.parser')
            canonical_tag = soup.find('link', rel='canonical')
            canonical_url = canonical_tag.get('href') if canonical_tag else ''
            canonical_match = "Match" if canonical_url == url else "Mismatch"
            meta_robots_tag = soup.find('meta', attrs={'name': 'robots'})
            meta_robots_content = meta_robots_tag['content'] if meta_robots_tag else ''
            csv_writer.writerow([url, response_code, canonical_url, canonical_match, meta_robots_content])
        else:
            csv_writer.writerow([url, response_code])

# Main function
def main():
    st.title("XML Sitemap Checker")
    url = st.text_input("Enter XML Sitemap URL:")
    user_agent = st.text_input("Enter User Agent:")
    if st.button("Check Sitemap"):
        domain = extract_domain(url)
        current_datetime = datetime.now().strftime("%m%d%Y_%H%M")
        csv_filename = f"{current_datetime}_{domain}_xml_sitemap_urls.csv"
        with open(csv_filename, 'w', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(["URL", "Response Code", "Canonical URL", "Canonical Match", "Meta Robots"])
            process_sitemap(url, user_agent, csv_writer)
        st.success(f"Process completed. CSV file: {csv_filename}")

if __name__ == "__main__":
    main()
