import os

import urllib
from requests_html import HTMLSession
from tqdm import tqdm
from time import sleep
import cv2
import numpy as np


def collect_images_from_dogs_page(session: HTMLSession, url: str, target_dir: str):
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

    table_cols_with_images = response.html.find('[bgcolor="#cccccc"]')

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
                    print(img_url)
                    print(f'Failed to read image {dst_img_path}')
                    print(f'Removed {dst_img_path}')
                    os.remove(dst_img_path)


if __name__ == '__main__':
    # Create an HTML session
    session = HTMLSession()

    # Define the URL
    url = 'https://dogsindepth.com/list_of_all_dog_breeds.html'

    # Define the headers
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'accept-language': 'ru-RU,ru;q=0.7',
        'cache-control': 'max-age=0',
        'if-modified-since': 'Wed, 13 Jan 2021 02:20:36 GMT',
        'if-none-match': '"4be0c86-3c4c-5b8bec8deb8ba-br"',
        'priority': 'u=0, i',
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

    # Make the request
    response = session.get(url, headers=headers)

    # Check the response status
    if response.status_code == 200:
        tr_list = response.html.find('tr[bgcolor="#cccccc"]')

        dogs_links = []

        for tr_element in tr_list:
            dogs_links.extend(tr_element.find('a'))

        for link in tqdm(dogs_links):
            collect_images_from_dogs_page(session, link.absolute_links.pop(), 'data/dogs_in_depth')
            sleep(1)

    else:
        print('Error while loading main page.')
