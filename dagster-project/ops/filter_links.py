from dagster import op


@op
def filter_links(dogs_links: list[str]) -> list[str]:
    used_links_list = []

    with open('data/used_links.txt', 'rt') as file:
        for line in file:
            used_links_list.append(line.strip())

    used_links_set = set(used_links_list)

    return [link for link in dogs_links if link not in used_links_set]
