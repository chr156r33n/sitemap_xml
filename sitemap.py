import streamlit as st
import requests
from datetime import datetime
from bs4 import BeautifulSoup
import csv
import os

# Function to extract the domain name from the URL
def extract_domain(url):
    return url.split('//')[-1].split('/')[0]

# Function to process XML sitemaps
def process_sitemap(url, user_agent):
    results = []
    response = requests.get(url, headers={'User-Agent': user_agent})
    soup = BeautifulSoup(response.content, 'xml')  # Specify 'xml' as the parser
    sitemap_tags = soup.find_all('sitemap')
    if sitemap_tags:
        for sitemap_tag in sitemap_tags:
            nested_sitemap_url = sitemap_tag.find('loc').text
            results.extend(process_sitemap(nested_sitemap_url, user_agent))
    else:
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
                results.append([url, response_code, canonical_url, canonical_match, meta_robots_content])
            else:
                results.append([url, response_code])
    return results

# Main function
def main():
    st.title("XML Sitemap Checker")
    url = st.text_input("Enter XML Sitemap URL:")
    user_agent = st.text_input("Enter User Agent:")
    if st.button("Check Sitemap"):
        domain = extract_domain(url)
        current_datetime = datetime.now().strftime("%m%d%Y_%H%M")
        csv_filename = f"{current_datetime}_{domain}_xml_sitemap_urls.csv"
        with st.spinner("Processing..."):
            results = process_sitemap(url, user_agent)
            with open(csv_filename, 'w', newline='') as csvfile:
                csv_writer = csv.writer(csvfile)
                csv_writer.writerow(["URL", "Response Code", "Canonical URL", "Canonical Match", "Meta Robots"])
                csv_writer.writerows(results)
            st.success("Process completed.")
            st.markdown(f"Download the CSV file: [link]({csv_filename})")

if __name__ == "__main__":
    main()
