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
def process_sitemap(url, user_agent, proxy=None, timeout=10):
    headers = {'User-Agent': user_agent}
    results = []
    try:
        response = requests.get(url, headers=headers, proxies=proxy, timeout=timeout)
        # Process the response...
    except requests.RequestException as e:
        st.error(f"Request error: {e}")
        return results

# Main function
def main():
    st.title("XML Sitemap Checker")
    url = st.text_input("Enter XML Sitemap URL:")
    default_user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36"
    user_agent = st.text_input("Enter User Agent:", default_user_agent)
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
