import os

import httpx
from loguru import logger

from src.feature_flags import flags
from src.utils import read_from_file, write_to_file


def scrape_and_convert_to_md(url: str) -> str:
    result = ""
    if flags.scrape:
        jina_url = "https://r.jina.ai/"

        new_url = jina_url + url
        response = httpx.get(
            new_url, headers={"Authorization": f"Bearer {os.getenv('JINA_API_KEY')}"}
        )

        if response.status_code == 200:
            result = response.content.decode("utf-8", errors="ignore")
        else:
            logger.error(
                f"Error scraping website: {response.status_code} - {response.text}"
            )
            result = ""
        if flags.save:
            write_to_file(result, "data/scraped.md")
    else:
        result = read_from_file("data/scraped.md")

    return result
