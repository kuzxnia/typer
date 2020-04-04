import requests
from bs4 import BeautifulSoup


def fetch_most_common_en_words():
    page = requests.get(
        "https://1000mostcommonwords.com/1000-most-common-english-words"
    )
    soup = BeautifulSoup(page.content, "html.parser")

    return [
        word
        for word in (
            td.get_text()
            for td in soup.find("div", {"class": "entry-content"}).find_all("td")
        )
        if word and not str(word).isnumeric()
    ]
