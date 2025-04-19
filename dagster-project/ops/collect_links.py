import logging

from dagster import op
from requests_html import HTMLSession, HTML



@op
def collect_links_from_dogs_in_depth():
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

    response = session.get(url, headers=headers)
    dogs_links = []

    # Check the response status
    if response.status_code == 200:
        # tr_list = response.html.find('tr[bgcolor="#cccccc"]')
        div_list = response.html.find('div[class="alphaTopicSection01"]') + response.html.find('div[class="alphaTopicSection02"]')

        for tr_element in div_list:
            dogs_links.extend(tr_element.find('a'))
    else:
        logging.error(f"Failed to fetch the page. Status code: {response.status_code}. {response.text}")

    return [item.absolute_links.pop() for item in dogs_links]


@op
def collect_links_from_dogstime() -> list[str]:
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

    logging.error(dogs_links)

    try:
        while True:
            response = session.get(url, params=params, headers=headers)

            logging.error(response)

            response_data = response.json()

            if response_data['data']['total_posts'] == 0:
                break

            posts_info = response_data['data']['posts']
            posts_html = HTML(html=posts_info)
            dogs_links.extend(list(posts_html.absolute_links))

            params['offset'] = str(int(params['offset']) + int(params['posts_per_page']))

    except Exception:
        pass

    logging.info(f'Collected {len(dogs_links)} links from DogTime')

    return dogs_links
