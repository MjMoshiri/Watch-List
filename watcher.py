import os
import time
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
# BUG: Single Image Listings
# TODO: Remove QR Code(and other irrelevant info) from posting body
def fetch_url_content(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.text

def parse_listing_page(content):
    soup = BeautifulSoup(content, "html.parser")
    return soup.find_all("li", class_="cl-static-search-result")

def extract_listing_ids(results, limit=10):
    ids = set()
    unprocessed = []
    for result, _ in zip(results, range(limit)):
        link = result.find("a")
        if link and "href" in link.attrs:
            listing_id = link["href"].split("/")[-1].split(".")[0]
            if listing_id not in ids:
                unprocessed.append(link["href"])
                ids.add(listing_id)
    return unprocessed

def process_listing(url):
    content = fetch_url_content(url)
    soup = BeautifulSoup(content, "html.parser")

    title_element = soup.find(id="titletextonly")
    if not title_element:
        print("Post deleted, skipping...")
        return

    title = title_element.get_text(strip=True)
    image_links = extract_image_links(soup)
    postingbody = extract_posting_body(soup)

    print("Title:", title)
    print("Images:", image_links)
    print("Body:", postingbody)
    print("----")

def extract_image_links(soup):
    image_links = []
    thumbs_div = soup.find("div", id="thumbs")
    if thumbs_div:
        for a in thumbs_div.find_all("a", class_="thumb"):
            if "href" in a.attrs:
                image_links.append(a["href"])
    else:
        img = soup.find("img", class_="first visible")
        if img and "src" in img.attrs:
            image_links.append(img["src"])
    return image_links

def extract_posting_body(soup):
    postingbody_section = soup.find("section", id="postingbody")
    if postingbody_section:
        return postingbody_section.get_text(strip=True, separator="\n")
    return ""

def main():
    load_dotenv()
    url = os.getenv("CRAGSLIST_URL")
    if not url:
        raise ValueError("CRAGSLIST_URL environment variable is not set")

    content = fetch_url_content(url)
    results = parse_listing_page(content)
    unprocessed = extract_listing_ids(results)

    for listing_url in unprocessed:
        print(f"Processing URL: {listing_url}")
        process_listing(listing_url)
        time.sleep(1)  # Sleep to avoid rate limiting

if __name__ == "__main__":
    main()
