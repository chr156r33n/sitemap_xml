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
def process_sitemap(url, user_agent, csv_writer):
    response = requests.get(url, headers={'User-Agent': user_agent})
    soup = BeautifulSoup(response.content, 'xml')  # Specify 'xml' as the parser
    sitemap_tags = soup.find_all('sitemap')
    if sitemap_tags:
        for sitemap_tag in sitemap_tags:
            nested_sitemap_url = sitemap_tag.find('loc').text
            st.write(f"Processing nested sitemap: {nested_sitemap_url}")
            process_sitemap(nested_sitemap_url, user_agent, csv_writer)
    else:
        for loc in soup.find_all('loc'):
            url = loc.text
            response = requests.head(url, headers={'User-Agent': user_agent})
            response_code = response.status_code
            if response_code == 200:
                st.write(f"Checking URL: {url}")
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
    user_agent = st.text_input("Enter User Agent:"
