import os
import time

import requests
from tqdm import tqdm
from bs4 import BeautifulSoup
from requests_html import HTMLSession, HTML

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options


def parse_dog_page(url, target_dir):
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=chrome_options)
    driver.set_page_load_timeout(time_to_wait=5)  # Hard timeout for page load

    try:
        driver.get(url)  # Will stop loading after 5 sec if not complete
    except TimeoutException:
        pass

    # Scroll down in increments (to trigger lazy-loaded content)
    scroll_pause_time = 1.0  # Adjust based on needs
    last_height = driver.execute_script("return document.body.scrollHeight")

    # Scroll for a fixed duration (e.g., 3 seconds)
    start_time = time.time()
    while time.time() - start_time < 3:  # Scroll for 3 seconds max
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(scroll_pause_time)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break  # Stop if no new content loads
        last_height = new_height

    # Get the HTML after scrolling
    html = driver.page_source

    soup = BeautifulSoup(html, 'lxml')

    # Step 1: Remove all divs with class "wp-block-xwp-curated-content"
    for div in soup.find_all('div', class_='wp-block-xwp-curated-content'):
        div.decompose()  # Remove the div from the tree

    for div in soup.find_all('details', class_='xe-breed-accordion'):
        div.decompose()  # Remove the div from the tree

    # Step 2: Extract all image links (src attributes)
    image_links = []
    for img in soup.find_all('img'):
        src = img.get('src')
        if src and src.startswith('https://dogtime.com/wp-content/uploads/'):
            image_links.append(src.split('?')[0])

    dog_name = url.split('/')[-1]
    target_dir = f"{target_dir}/{dog_name}"

    os.makedirs(target_dir, exist_ok=True)

    # Step 3: Save the image links to target directory
    for i, link in enumerate(image_links):
        filename = f"{target_dir}/{dog_name}_{i}.{link.split('/')[-1].split('.')[-1]}"
        
        with open(filename, 'wb') as f:
            f.write(requests.get(link).content)

    if len(image_links) > 8:
        print('Too many images')
        print(url)


if __name__ == '__main__':
    url = "https://dogtime.com/dog-breeds/xwp_curated_content"

    params = {
        "index_primary": "",
        "search": "",
        "xwp_curated_content_posts": "",
        "block_id": "02f15b39-5275-4c9e-ae23-2fe8460c481e",
        "post_id": "110743",
        "offset": "0",
        "posts_per_page": "12",
        "action": "filter"
    }

    headers = {
        "sec-ch-ua-platform": "macOS",
        "Referer": "https://dogtime.com/dog-breeds",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "sec-ch-ua": '"Brave";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        "sec-ch-ua-mobile": "?0"
    }

    session = HTMLSession()

    dogs_links = []

    while True:
        response = session.get(url, params=params, headers=headers)

        response_data = response.json()

        if response_data['data']['total_posts'] == 0:
            break

        posts_info = response_data['data']['posts']
        posts_html = HTML(html=posts_info)
        dogs_links.extend(list(posts_html.absolute_links))

        params['offset'] = str(int(params['offset']) + int(params['posts_per_page']))

    print("Total dogs:", len(dogs_links))

    for link in tqdm(dogs_links):
        while True:
            try:
                parse_dog_page(link, 'data/dogtime')
            except Exception:
                time.sleep(5)
                continue
            break
    