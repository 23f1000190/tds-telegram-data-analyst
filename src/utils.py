import re


def extract_url(text):
    urls = re.findall(
        r'https?://\S+',
        text
    )

    if urls:
        return urls[0]

    return None
