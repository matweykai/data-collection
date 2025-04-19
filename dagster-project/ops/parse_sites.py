import os
import time
import logging

import cv2
import requests
from dagster import op
from bs4 import BeautifulSoup
from requests_html import HTMLSession

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options


@op
def parse_dog_time_link(url, target_data_dir):
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
    target_dir = f"{target_data_dir}/{dog_name}"

    os.makedirs(target_dir, exist_ok=True)

    # Step 3: Save the image links to target directory
    for i, link in enumerate(image_links):
        filename = f"{target_dir}/{dog_name}_{i}.{link.split('/')[-1].split('.')[-1]}"
        
        with open(filename, 'wb') as f:
            f.write(requests.get(link).content)


@op
def parse_dogs_in_depth_link(url, target_dir):
    session = HTMLSession()

    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'accept-language': 'ru-RU,ru;q=0.7',
        'cache-control': 'max-age=0',
        'if-modified-since': 'Wed, 13 Jan 2021 02:20:36 GMT',
        'if-none-match': '"4be0c86-3c4c-5b8bec8deb8ba-br"',
        'priority': 'u=0, i',
        'referer': 'https://dogsindepth.com/list_of_all_dog_breeds.html',
        'sec-ch-ua': '"Brave";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'sec-gpc': '1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
    }

    response = session.get(url, headers=headers)

    dog_name = response.html.find('h1', first=True).text

    table_cols_with_images = response.html.find('div[class="slider-container"]')

    imgs_links = []

    for col in table_cols_with_images:
        imgs_links.extend(col.find('img'))

    if len(imgs_links) > 3:
        dog_subfolder = target_dir + '/' + dog_name.replace(' ', '_')

        os.makedirs(dog_subfolder, exist_ok=True)

        for img_link in imgs_links:
            rel_img_url = img_link.attrs['src']

            if rel_img_url.endswith('.jpg'):
                img_url = response.html._make_absolute(rel_img_url)

                img_resp = session.get(img_url, headers=headers)
                img_name = img_url.split('/')[-1]

                dst_img_path = dog_subfolder + '/' + img_name

                with open(dst_img_path, 'wb') as f:
                    f.write(img_resp.content)

                img = cv2.imread(dst_img_path)
                if img is None:
                    logging.error(img_url)
                    logging.error(f'Failed to read image {dst_img_path}')
                    logging.error(f'Removed {dst_img_path}')
                    os.remove(dst_img_path)
