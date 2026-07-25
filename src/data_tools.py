import pandas as pd
import requests
import io


def load_dataset(url):
    response = requests.get(url)
    response.raise_for_status()

    content = response.content

    if url.endswith(".csv"):
        df = pd.read_csv(io.BytesIO(content))

    elif url.endswith(".xlsx") or url.endswith(".xls"):
        df = pd.read_excel(io.BytesIO(content))

    else:
        raise ValueError("Unsupported dataset format")

    return df
