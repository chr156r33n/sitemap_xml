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
def process_sitemap(url, user_agent, proxy=None, timeout=30):
    results = []
    response = requests.get(url, headers={'User-Agent': user_agent}, proxies=proxy, timeout=timeout)
    if response.status_code != 200:
        st.error(f"Error: Sitemap URL returned status code {response.status_code}")
        return results
    soup = BeautifulSoup(response.content, 'xml')  # Specify 'xml' as the parser
    sitemap_tags = soup.find_all('sitemap')
    if sitemap_tags:
        for sitemap_tag in sitemap_tags:
            nested_sitemap_url = sitemap_tag.find('loc').text
            results.extend(process_sitemap(nested_sitemap_url, user_agent, proxy, timeout))
    else:
        for loc in soup.find_all('loc'):
            url = loc.text
            try:
                response = requests.head(url, headers={'User-Agent': user_agent}, proxies=proxy, timeout=timeout)
                response_code = response.status_code
                if response_code == 200:
                    page_response = requests.get(url, headers={'User-Agent': user_agent}, proxies=proxy, timeout=timeout)
                    page_content = page_response.content
                    soup = BeautifulSoup(page_content, 'html.parser')
                    canonical_tag = soup.find('link', rel='canonical')
                    canonical_url = canonical_tag.get('href') if canonical_tag else ''
                    canonical_match = "Match" if canonical_url == url else "Mismatch"
                    meta_robots_tag = soup.find('meta', attrs={'name': 'robots'})
                    meta_robots_content = meta_robots_tag['content'] if meta_robots_tag else ''
                    results.append([url, response_code, canonical_url, canonical_match, meta_robots_content])
                    st.write(f"Checked URL: {url}")
                else:
                    results.append([url, response_code])
                    st.write(f"Checked URL: {url} (Response code: {response_code})")
            except requests.Timeout:
                st.write(f"Timed out while checking URL: {url}")
            except Exception as e:
                st.write(f"Error occurred while checking URL: {url} - {e}")
    return results

# Main function
def main():
    st.title("XML Sitemap Checker")
    url = st.text_input("Enter XML Sitemap URL:")
    user_agent = st.text_input("Enter User Agent(optional):")
    proxy = st.text_input("Enter Proxy (optional):")
    if st.button("Check Sitemap"):
        domain = extract_domain(url)
        current_datetime = datetime.now().strftime("%m%d%Y_%H%M")
        csv_filename = f"{current_datetime}_{domain}_xml_sitemap_urls.csv"
        proxy_dict = {"http": proxy, "https": proxy} if proxy else None
        with st.spinner("Processing..."):
            results = process_sitemap(url, user_agent, proxy=proxy_dict)
            if results:
                with open(csv_filename, 'w', newline='') as csvfile:
                    csv_writer = csv.writer(csvfile)
                    csv_writer.writerow(["URL", "Response Code", "Canonical URL", "Canonical Match", "Meta Robots"])
                    csv_writer.writerows(results)
                st.success("Process completed.")

                # Provide a download button to download the file
                with open(csv_filename, 'rb') as f:
                    st.download_button(
                        label="Download CSV File",
                        data=f,
                        file_name=csv_filename,
                        mime="text/csv"
                    )
            else:
                st.error("Process failed. Please check the provided sitemap URL.")

if __name__ == "__main__":
    main()
